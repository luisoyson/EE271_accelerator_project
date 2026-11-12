"""PE instruction set at the abstraction level of the spec (section 3.1).

What each instruction *does*, never how it is encoded: there are no opcode
numbers or bit patterns here, because decoding them is part of the graded
work. Field widths come from the course's own instruction configuration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.compiler import generate_accelerator_and_instruction_configuration
from src.instruction import PEI

# Datapath pieces the viewer draws inside a PE. An instruction lists the ones
# it uses; the viewer highlights them.
PATHS: frozenset[str] = frozenset({
    "in_a", "in_b", "value",
    "mul", "add", "sext", "rnd", "zero", "clamp",
    "acc", "out",
    "a_mul", "b_mul", "mul_add", "acc_add", "add_acc",
    "a_sext", "sext_acc",
    "acc_rnd", "value_rnd", "rnd_acc",
    "zero_acc", "zero_out",
    "acc_clamp", "clamp_out",
})


@dataclass(frozen=True)
class OpInfo:
    """One PE instruction, described by its effect (paraphrasing the spec)."""

    name: str
    summary: str
    reads: str
    accumulator: str
    output: str
    active: tuple[str, ...]


PE_OPS: tuple[OpInfo, ...] = (
    OpInfo(
        "MAC",
        "Multiply-and-accumulate, in every lane at once.",
        "Inputs A and B",
        "Each lane += (A lane × B lane), using the full signed product. Does not saturate.",
        "Unchanged",
        ("in_a", "in_b", "a_mul", "b_mul", "mul", "mul_add", "add", "acc_add", "add_acc", "acc"),
    ),
    OpInfo(
        "NOP",
        "Do nothing.",
        "Nothing",
        "Unchanged",
        "Unchanged",
        (),
    ),
    OpInfo(
        "OUT",
        "Copy the accumulator to the output register, clamping each lane so it fits.",
        "Accumulator",
        "Unchanged (only the copy is clamped)",
        "Each accumulator lane clamped to the output lane's signed range, lanes kept in order",
        ("acc", "acc_clamp", "clamp", "clamp_out", "out"),
    ),
    OpInfo(
        "PASS",
        "Load input A straight into the accumulator.",
        "Input A (the MEM1 broadcast)",
        "Each lane = the matching A lane, sign-extended to the wider accumulator lane",
        "Unchanged",
        ("in_a", "a_sext", "sext", "sext_acc", "acc"),
    ),
    OpInfo(
        "CLR",
        "Clear everything.",
        "Nothing",
        "Set to zero",
        "Set to zero",
        ("zero", "zero_acc", "zero_out", "acc", "out"),
    ),
    OpInfo(
        "RND",
        "Scale the accumulator down by a power of two, rounding.",
        "Accumulator and the Value field (s)",
        "Each lane = lane ÷ 2^s, rounded to the nearest integer, ties to even",
        "Unchanged",
        ("acc", "acc_rnd", "value", "value_rnd", "rnd", "rnd_acc"),
    ),
)

MODE_NAMES: dict[int, str] = {8: "INT8", 16: "INT16", 32: "INT32"}


def pe_isa() -> dict[str, Any]:
    """Return the PE instruction format and instruction table, JSON-ready."""
    _accel, inst = generate_accelerator_and_instruction_configuration()
    pe = inst.PE_INST_CONFIG
    value_max = 2 ** pe.VALUE_BITWIDTH - 1
    return {
        "fields": [
            {"name": "Opcode", "bits": pe.OPCODE_BITWIDTH,
             "meaning": "Which operation the PE performs."},
            {"name": "Mode", "bits": pe.MODE_BITWIDTH,
             "meaning": "How to split each word into lanes: INT8 (4 lanes), INT16 (2) or INT32 (1)."},
            {"name": "Value", "bits": pe.VALUE_BITWIDTH,
             "meaning": f"An unsigned number 0–{value_max}. RND uses it as the shift s."},
        ],
        "total_bits": pe.get_width(),
        "value_max": value_max,
        "modes": [{"bits": b, "name": n} for b, n in MODE_NAMES.items()],
        "ops": [asdict(op) for op in PE_OPS],
        "notes": [
            "Every PE receives the same instruction (SIMD).",
            "Only OUT and CLR change the output register.",
            "In INT8/INT16, each lane is computed independently.",
        ],
    }


def isa_op_names() -> set[str]:
    """Instruction names the course assembler accepts (for consistency checks)."""
    return set(PEI.STR_TO_OPCODE_DICT)
