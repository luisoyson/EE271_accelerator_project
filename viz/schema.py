"""Trace schema v0: the contract between the recorder (backend) and the viewer.

A trace is one simulator run, recorded as a list of *events*. Each event is
one call the accelerator made into a component (the main buffer or one PE),
with the state of that component right after the call. Events appear in the
order the calls happened, so the trace shows whatever ordering the simulator
uses rather than assuming one. Full field reference: docs/trace_schema.md.

Run ``python -m viz.schema <dir>`` to validate every ``*.json`` in a folder.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from viz.configs import PRESETS, preset_config

SCHEMA_VERSION = 0
MEM_OPCODES = frozenset({"READ", "WRITE", "NOP"})
PE_OPCODES = frozenset({"MAC", "NOP", "OUT", "PASS", "CLR", "RND"})
PE_STATE_KEYS = ("input_a", "input_b", "acc", "out")
RND_VALUE_MAX = 31  # Value field is 5 bits, unsigned
_HEX = re.compile(r"0x[0-9a-f]+")


class TraceError(ValueError):
    """A trace does not match the schema. The message starts with the path."""

    def __init__(self, path: str, problem: str) -> None:
        super().__init__(f"{path}: {problem}")
        self.path = path


# ---------------------------------------------------------------- primitives

def _obj(value: Any, path: str, keys: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TraceError(path, f"expected an object, got {type(value).__name__}")
    missing = [k for k in keys if k not in value]
    if missing:
        raise TraceError(path, f"missing key(s) {missing}")
    return value


def _int(value: Any, path: str, lo: int | None = None, hi: int | None = None) -> int:
    # bool is a subclass of int in Python; reject it explicitly.
    if not isinstance(value, int) or isinstance(value, bool):
        raise TraceError(path, f"expected an integer, got {value!r}")
    if lo is not None and value < lo:
        raise TraceError(path, f"{value} is below the minimum {lo}")
    if hi is not None and value > hi:
        raise TraceError(path, f"{value} is above the maximum {hi}")
    return value


def _list(value: Any, path: str, length: int | None = None) -> list[Any]:
    if not isinstance(value, list):
        raise TraceError(path, f"expected a list, got {type(value).__name__}")
    if length is not None and len(value) != length:
        raise TraceError(path, f"expected {length} item(s), got {len(value)}")
    return value


def _choice(value: Any, path: str, allowed: frozenset[str] | set[str]) -> str:
    if value not in allowed:
        raise TraceError(path, f"{value!r} is not one of {sorted(allowed)}")
    return value


# --------------------------------------------------------------------- words

def validate_word(word: Any, bits: int, lanes: int, path: str) -> None:
    """Check one register/port value.

    A word is ``{"bits": int, "lanes": [int, ...], "hex": str | null}``.
    ``lanes`` are signed values, least-significant lane first, each within
    the signed range of ``bits // lanes`` bits. ``hex`` is the raw word,
    lowercase, zero-padded to ``bits // 4`` digits, or null.

    Note: v0 does not check that ``hex`` and ``lanes`` agree. That check
    needs lane packing, which is part of the graded work; it is added once
    the recorder exists.
    """
    w = _obj(word, path, ("bits", "lanes", "hex"))
    if _int(w["bits"], f"{path}.bits") != bits:
        raise TraceError(f"{path}.bits", f"expected {bits}, got {w['bits']}")
    lane_bits = bits // lanes
    lo, hi = -(2 ** (lane_bits - 1)), 2 ** (lane_bits - 1) - 1
    values = _list(w["lanes"], f"{path}.lanes", lanes)
    for i, v in enumerate(values):
        _int(v, f"{path}.lanes[{i}]", lo, hi)
    raw = w["hex"]
    if raw is not None:
        if not isinstance(raw, str) or not _HEX.fullmatch(raw):
            raise TraceError(f"{path}.hex", f"expected lowercase '0x…' hex or null, got {raw!r}")
        if len(raw) - 2 != bits // 4:
            raise TraceError(f"{path}.hex", f"expected {bits // 4} hex digits, got {len(raw) - 2}")


# -------------------------------------------------------------------- events

def _validate_mem_event(ev: dict[str, Any], path: str, cfg: dict[str, Any]) -> None:
    instr = _obj(ev["instr"], f"{path}.instr", ("opcode", "mode", "mema_offset", "memb_offset"))
    _choice(instr["opcode"], f"{path}.instr.opcode", MEM_OPCODES)
    geo = _mode_geometry(instr["mode"], f"{path}.instr.mode", cfg)
    _int(instr["mema_offset"], f"{path}.instr.mema_offset", 0)
    _int(instr["memb_offset"], f"{path}.instr.memb_offset", 0)

    in_bits, out_bits = cfg["pe"]["input_bitwidth"], cfg["pe"]["output_bitwidth"]
    n_pe, lanes = cfg["pe_count"], geo["lanes"]
    state = _obj(ev["state"], f"{path}.state", ("mem0_port", "mem1_port", "mem2_write"))
    for i, word in enumerate(_list(state["mem0_port"], f"{path}.state.mem0_port", n_pe)):
        validate_word(word, in_bits, lanes, f"{path}.state.mem0_port[{i}]")
    validate_word(state["mem1_port"], in_bits, lanes, f"{path}.state.mem1_port")
    if state["mem2_write"] is not None:
        wp = f"{path}.state.mem2_write"
        write = _obj(state["mem2_write"], wp, ("addr", "words"))
        _int(write["addr"], f"{wp}.addr", 0, cfg["memories"]["mem2"]["depth"] - 1)
        for i, word in enumerate(_list(write["words"], f"{wp}.words", n_pe)):
            validate_word(word, out_bits, lanes, f"{wp}.words[{i}]")


def _validate_pe_event(ev: dict[str, Any], path: str, cfg: dict[str, Any]) -> None:
    if "pe" not in ev:
        raise TraceError(path, "pe events need a 'pe' index")
    _int(ev["pe"], f"{path}.pe", 0, cfg["pe_count"] - 1)
    instr = _obj(ev["instr"], f"{path}.instr", ("opcode", "mode", "value"))
    _choice(instr["opcode"], f"{path}.instr.opcode", PE_OPCODES)
    geo = _mode_geometry(instr["mode"], f"{path}.instr.mode", cfg)
    _int(instr["value"], f"{path}.instr.value", 0, RND_VALUE_MAX)

    pe, lanes = cfg["pe"], geo["lanes"]
    widths = {
        "input_a": pe["input_bitwidth"],
        "input_b": pe["input_bitwidth"],
        "acc": pe["accumulation_bitwidth"],
        "out": pe["output_bitwidth"],
    }
    state = _obj(ev["state"], f"{path}.state", PE_STATE_KEYS)
    for key in PE_STATE_KEYS:
        validate_word(state[key], widths[key], lanes, f"{path}.state.{key}")


def _mode_geometry(mode: Any, path: str, cfg: dict[str, Any]) -> dict[str, int]:
    _int(mode, path)
    key = str(mode)
    if key not in cfg["modes"]:
        raise TraceError(path, f"{mode} is not one of {sorted(int(m) for m in cfg['modes'])}")
    return cfg["modes"][key]


# --------------------------------------------------------------------- trace

def validate_trace(trace: Any) -> dict[str, Any]:
    """Validate a parsed trace and return the config of its preset.

    Raises:
        TraceError: naming the first offending field, e.g.
            ``events[3].state.acc.lanes[1]: 2147483648 is above the maximum``.
    """
    t = _obj(trace, "trace", ("schema_version", "synthetic", "description", "preset", "events"))
    if t["schema_version"] != SCHEMA_VERSION:
        raise TraceError("schema_version", f"expected {SCHEMA_VERSION}, got {t['schema_version']!r}")
    if not isinstance(t["synthetic"], bool):
        raise TraceError("synthetic", f"expected true/false, got {t['synthetic']!r}")
    if not isinstance(t["description"], str):
        raise TraceError("description", "expected a string")
    _choice(t["preset"], "preset", set(PRESETS))
    cfg = preset_config(t["preset"])

    last_instr = 0
    for i, ev in enumerate(_list(t["events"], "events")):
        path = f"events[{i}]"
        e = _obj(ev, path, ("seq", "instr_index", "repeat", "component", "instr", "state"))
        if _int(e["seq"], f"{path}.seq") != i:
            raise TraceError(f"{path}.seq", f"expected {i} (events must be in order), got {e['seq']}")
        idx = _int(e["instr_index"], f"{path}.instr_index", 0)
        if idx < last_instr:
            raise TraceError(f"{path}.instr_index", f"went backwards from {last_instr} to {idx}")
        last_instr = idx
        _int(e["repeat"], f"{path}.repeat", 0)
        component = _choice(e["component"], f"{path}.component", {"mem", "pe"})
        if component == "mem":
            _validate_mem_event(e, path, cfg)
        else:
            _validate_pe_event(e, path, cfg)
    return cfg


def load_trace(path: Path) -> dict[str, Any]:
    """Read and validate a trace file.

    Raises:
        OSError: if the file cannot be read.
        TraceError: if the file is not valid JSON or not a valid trace.
    """
    try:
        trace = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TraceError(path.name, f"not valid JSON ({exc.msg}, line {exc.lineno})") from exc
    validate_trace(trace)
    return trace


def main(argv: list[str]) -> int:
    """Validate every ``*.json`` in the given folders. Returns an exit code."""
    if not argv:
        print("usage: python -m viz.schema <folder> [<folder> ...]", file=sys.stderr)
        return 2
    failures = 0
    files = sorted(f for d in argv for f in Path(d).glob("*.json"))
    for f in files:
        try:
            load_trace(f)
            print(f"ok    {f}")
        except (OSError, TraceError) as exc:
            failures += 1
            print(f"FAIL  {f}: {exc}", file=sys.stderr)
    print(f"{len(files) - failures}/{len(files)} trace(s) valid")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
