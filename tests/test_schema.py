"""Trace schema v0: the sample is valid, and each kind of malformed trace is
rejected with an error that names where it went wrong."""

import copy
import json
from pathlib import Path
from typing import Any, Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st

from viz.schema import TraceError, validate_trace, validate_word

SAMPLE = Path(__file__).resolve().parent.parent / "traces" / "sample.json"


@pytest.fixture
def trace() -> dict[str, Any]:
    return json.loads(SAMPLE.read_text())


def test_sample_trace_is_valid(trace: dict[str, Any]) -> None:
    validate_trace(trace)


def _set(path: list[Any], value: Any) -> Callable[[dict[str, Any]], None]:
    def mutate(t: dict[str, Any]) -> None:
        node = t
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
    return mutate


def _delete(path: list[Any]) -> Callable[[dict[str, Any]], None]:
    def mutate(t: dict[str, Any]) -> None:
        node = t
        for key in path[:-1]:
            node = node[key]
        del node[path[-1]]
    return mutate


BAD_TRACES = [
    ("wrong version", _set(["schema_version"], 1), r"schema_version"),
    ("unknown preset", _set(["preset"], "nope"), r"preset"),
    ("synthetic not bool", _set(["synthetic"], "yes"), r"synthetic"),
    ("seq out of order", _set(["events", 2, "seq"], 7), r"events\[2\]\.seq"),
    ("instr_index goes backwards", _set(["events", 6, "instr_index"], 0), r"events\[6\]\.instr_index"),
    ("bad component", _set(["events", 0, "component"], "alu"), r"events\[0\]\.component"),
    ("pe index out of range", _set(["events", 1, "pe"], 4), r"events\[1\]\.pe"),
    ("pe opcode on pe", _set(["events", 1, "instr", "opcode"], "READ"), r"events\[1\]\.instr\.opcode"),
    ("mem opcode on mem", _set(["events", 0, "instr", "opcode"], "MAC"), r"events\[0\]\.instr\.opcode"),
    ("bad mode", _set(["events", 1, "instr", "mode"], 4), r"events\[1\]\.instr\.mode"),
    ("rnd value too big", _set(["events", 1, "instr", "value"], 32), r"events\[1\]\.instr\.value"),
    ("negative offset", _set(["events", 0, "instr", "mema_offset"], -1), r"mema_offset"),
    ("too many lanes", _set(["events", 1, "state", "acc", "lanes"], [0, 0, 0]), r"events\[1\]\.state\.acc\.lanes"),
    ("acc lane overflow", _set(["events", 1, "state", "acc", "lanes"], [2**31, 0]), r"acc\.lanes\[0\]"),
    ("out lane underflow", _set(["events", 1, "state", "out", "lanes"], [0, -(2**15) - 1]), r"out\.lanes\[1\]"),
    ("wrong word width", _set(["events", 1, "state", "acc", "bits"], 32), r"acc\.bits"),
    ("hex wrong length", _set(["events", 1, "state", "out", "hex"], "0x0"), r"out\.hex"),
    ("hex not hex", _set(["events", 1, "state", "out", "hex"], "0xzzzzzzzz"), r"out\.hex"),
    ("mem0 port wrong count", _set(["events", 0, "state", "mem0_port"], []), r"mem0_port"),
    ("mem2 write wrong count", _set(["events", 0, "state", "mem2_write"], {"addr": 0, "words": []}), r"mem2_write"),
    ("missing state key", _delete(["events", 1, "state", "input_b"]), r"events\[1\]\.state"),
    ("bool is not int", _set(["events", 1, "pe"], True), r"events\[1\]\.pe"),
]


@pytest.mark.parametrize(("label", "mutate", "where"), BAD_TRACES, ids=[b[0] for b in BAD_TRACES])
def test_malformed_traces_are_rejected(
    trace: dict[str, Any], label: str, mutate: Callable[[dict[str, Any]], None], where: str
) -> None:
    bad = copy.deepcopy(trace)
    mutate(bad)
    with pytest.raises(TraceError, match=where):
        validate_trace(bad)


@given(st.data(), st.sampled_from([(8, 4), (16, 2), (32, 1)]), st.sampled_from([32, 64]))
def test_word_accepts_exactly_the_signed_lane_range(data: st.DataObject, mode_lanes: tuple[int, int], bits: int) -> None:
    _mode, lanes = mode_lanes
    lane_bits = bits // lanes
    lo, hi = -(2 ** (lane_bits - 1)), 2 ** (lane_bits - 1) - 1
    values = data.draw(st.lists(st.integers(lo, hi), min_size=lanes, max_size=lanes))
    validate_word({"bits": bits, "lanes": values, "hex": None}, bits, lanes, "w")

    i = data.draw(st.integers(0, lanes - 1))
    values[i] = data.draw(st.sampled_from([lo - 1, hi + 1]))
    with pytest.raises(TraceError, match=rf"w\.lanes\[{i}\]"):
        validate_word({"bits": bits, "lanes": values, "hex": None}, bits, lanes, "w")
