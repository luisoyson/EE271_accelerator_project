"""The visualizer mirrors a few course formulas instead of importing
compiler.py (which imports the graded files). These tests compare the mirror
with the real thing. They skip, with the reason shown, while a graded file
does not import, e.g. mid-edit with a syntax error."""

import pytest

from viz.configs import PRESETS, preset_config
from viz.isa import pe_isa


@pytest.fixture(scope="module")
def generator():
    try:
        from src.compiler import generate_accelerator_and_instruction_configuration
    except Exception as exc:  # any import-time failure in a graded file
        pytest.skip(f"course modules don't import yet ({type(exc).__name__}: {exc})")
    return generate_accelerator_and_instruction_configuration


@pytest.mark.parametrize("name", list(PRESETS))
def test_preset_matches_course_generator(generator, name: str) -> None:
    p = PRESETS[name]
    accel, _inst = generator(
        processing_element_count=p.pe_count,
        processing_element_accumulation_bitwidth=p.accumulation_bitwidth,
        controller_counter_bitwidth=p.counter_bitwidth,
    )
    accel.validate()
    cfg = preset_config(name)
    buf = accel.BUFFER_CONFIG
    assert cfg["pe_count"] == accel.PE_COUNT
    assert cfg["pe"] == {
        "input_bitwidth": accel.PE_CONFIG.INPUT_BITWIDTH,
        "accumulation_bitwidth": accel.PE_CONFIG.ACCUMULATION_BITWIDTH,
        "output_bitwidth": accel.PE_CONFIG.OUTPUT_BITWIDTH,
    }
    assert cfg["memories"] == {
        "mem0": {"bitwidth": buf.MEM0_BITWIDTH, "depth": buf.MEM0_DEPTH},
        "mem1": {"bitwidth": buf.MEM1_BITWIDTH, "depth": buf.MEM1_DEPTH},
        "mem2": {"bitwidth": buf.MEM2_BITWIDTH, "depth": buf.MEM2_DEPTH},
    }


def test_pe_instruction_widths_match_course(generator) -> None:
    _accel, inst = generator()
    pe = inst.PE_INST_CONFIG
    widths = [f["bits"] for f in pe_isa()["fields"]]
    assert widths == [pe.OPCODE_BITWIDTH, pe.MODE_BITWIDTH, pe.VALUE_BITWIDTH]
