"""PE instruction reference: matches the course ISA, and reveals no encodings."""

import json

from viz.isa import PATHS, PE_OPS, isa_op_names, pe_isa


def test_fields_match_course_instruction_config() -> None:
    isa = pe_isa()
    assert [(f["name"], f["bits"]) for f in isa["fields"]] == [("Opcode", 2), ("Mode", 2), ("Value", 5)]
    assert isa["total_bits"] == 9
    assert isa["value_max"] == 31  # spec: s in {0, ..., 31}


def test_table_covers_exactly_the_assembler_instructions() -> None:
    assert {op.name for op in PE_OPS} == isa_op_names()


def test_every_highlighted_path_exists() -> None:
    for op in PE_OPS:
        assert set(op.active) <= PATHS, op.name


def test_only_out_and_clr_change_the_output_register() -> None:
    # Spec 3.1: "Among PE instructions, only OUT and CLR update the output register."
    changes_out = {op.name for op in PE_OPS if op.output != "Unchanged"}
    assert changes_out == {"OUT", "CLR"}
    assert {op.name for op in PE_OPS if "out" in op.active} == {"OUT", "CLR"}


def test_no_encodings_are_exposed() -> None:
    # Decoding is graded work: the reference must not carry opcode numbers.
    text = json.dumps(pe_isa()).lower()
    for leak in ("encoding", "opcode_value", "no_value", "0b"):
        assert leak not in text
