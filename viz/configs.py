"""Accelerator configurations the visualizer can draw.

Configs are built with the course's own
``generate_accelerator_and_instruction_configuration`` so the drawing always
matches what the tests instantiate. Lane geometry is computed here, in the
backend, so the frontend only draws.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.compiler import generate_accelerator_and_instruction_configuration
from src.instruction import Mode

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

    accel, _inst = generate_accelerator_and_instruction_configuration(
        processing_element_count=preset.pe_count,
        processing_element_accumulation_bitwidth=preset.accumulation_bitwidth,
        controller_counter_bitwidth=preset.counter_bitwidth,
    )
    accel.validate()
    pe, buf = accel.PE_CONFIG, accel.BUFFER_CONFIG
    return {
        "preset": name,
        "description": preset.description,
        "default_mode": preset.default_mode,
        "pe_count": accel.PE_COUNT,
        "counter_bitwidth": accel.COUNTER_BITWIDTH,
        "pe": {
            "input_bitwidth": pe.INPUT_BITWIDTH,
            "accumulation_bitwidth": pe.ACCUMULATION_BITWIDTH,
            "output_bitwidth": pe.OUTPUT_BITWIDTH,
        },
        "memories": {
            "mem0": {"bitwidth": buf.MEM0_BITWIDTH, "depth": buf.MEM0_DEPTH},
            "mem1": {"bitwidth": buf.MEM1_BITWIDTH, "depth": buf.MEM1_DEPTH},
            "mem2": {"bitwidth": buf.MEM2_BITWIDTH, "depth": buf.MEM2_DEPTH},
        },
        "modes": {
            str(m): lane_geometry(
                pe.INPUT_BITWIDTH, pe.ACCUMULATION_BITWIDTH, pe.OUTPUT_BITWIDTH, m
            )
            for m in MODES
        },
    }


def preset_list() -> list[dict[str, str]]:
    """Return ``[{name, description}]`` for every preset."""
    return [{"name": n, "description": p.description} for n, p in PRESETS.items()]
