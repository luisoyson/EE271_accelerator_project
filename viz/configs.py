"""Accelerator configurations the visualizer can draw.

Configs mirror the course's ``generate_accelerator_and_instruction_configuration``
(src/compiler.py) formula for formula. They are not built by calling it,
because compiler.py imports the graded files, and the visualizer must keep
working while those are half-written. tests/test_course_consistency.py checks
the mirror against the real generator whenever the graded files import.

Lane geometry is computed here, in the backend, so the frontend only draws.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.instruction import Mode  # imports no graded file

# Fixed by the course ISA / compiler defaults.
PE_INPUT_BITWIDTH = 32
PE_OUTPUT_BITWIDTH = 32

MODES: tuple[int, ...] = (Mode.INT8, Mode.INT16, Mode.INT32)


@dataclass(frozen=True)
class Preset:
    """Arguments for the course config generator, plus a display default."""

    description: str
    pe_count: int
    accumulation_bitwidth: int
    counter_bitwidth: int
    default_mode: int


PRESETS: dict[str, Preset] = {
    "demo-4pe": Preset("Small demo: 4 PEs", 4, 64, 10, Mode.INT16),
    "test-int16-64pe": Preset("test_accelerator.py: 64 PEs, INT16", 64, 64, 16, Mode.INT16),
    "test-int32-13pe": Preset("test_accelerator.py: 13 PEs, INT32", 13, 64, 16, Mode.INT32),
    "test-int8-9pe": Preset("test_accelerator.py: 9 PEs, INT8", 9, 64, 16, Mode.INT8),
}

DEFAULT_PRESET = "demo-4pe"


class UnknownPresetError(KeyError):
    """Raised when a preset name is not in :data:`PRESETS`."""


def lane_geometry(input_bw: int, acc_bw: int, output_bw: int, mode: int) -> dict[str, int]:
    """Return lane count and per-lane widths for one mode.

    In a mode of ``mode`` bits, each 32-bit input word holds
    ``input_bw // mode`` lanes, and the accumulator and output registers are
    split into the same number of (wider or equal) lanes.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode}")
    lanes = input_bw // mode
    return {
        "lanes": lanes,
        "input_lane_bits": mode,
        "acc_lane_bits": acc_bw // lanes,
        "output_lane_bits": output_bw // lanes,
    }


def preset_config(name: str) -> dict[str, Any]:
    """Return a JSON-ready description of preset ``name``.

    Raises:
        UnknownPresetError: if ``name`` is not a known preset.
    """
    try:
        preset = PRESETS[name]
    except KeyError:
        raise UnknownPresetError(name) from None

    n, counter = preset.pe_count, preset.counter_bitwidth
    in_bw, acc_bw, out_bw = PE_INPUT_BITWIDTH, preset.accumulation_bitwidth, PE_OUTPUT_BITWIDTH
    # Same formulas as compiler.generate_accelerator_and_instruction_configuration.
    mem1_depth = 2 ** (counter - math.ceil(math.log2(in_bw / Mode.SMALLEST_MODE)))
    return {
        "preset": name,
        "description": preset.description,
        "default_mode": preset.default_mode,
        "pe_count": n,
        "counter_bitwidth": counter,
        "pe": {
            "input_bitwidth": in_bw,
            "accumulation_bitwidth": acc_bw,
            "output_bitwidth": out_bw,
        },
        "memories": {
            "mem0": {"bitwidth": n * in_bw, "depth": 2 ** counter},
            "mem1": {"bitwidth": in_bw, "depth": mem1_depth},
            "mem2": {"bitwidth": n * out_bw, "depth": 2 ** counter},
        },
        "modes": {str(m): lane_geometry(in_bw, acc_bw, out_bw, m) for m in MODES},
    }


def preset_list() -> list[dict[str, str]]:
    """Return ``[{name, description}]`` for every preset."""
    return [{"name": n, "description": p.description} for n, p in PRESETS.items()]
