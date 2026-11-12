"""A map of the course starter code, read live from ``simd-part1/src``.

Structure only: which files, classes and methods exist, how they relate, and
the Python idioms they use. Graded methods are reported as ``todo`` while they
still contain the course's "Your Code Here" marker and ``written`` after, so
the map doubles as a progress tracker. Nothing here describes *how* to
implement a graded method.
"""

from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SRC_DIR = Path(__file__).resolve().parent.parent / "simd-part1" / "src"
TODO_MARKER = "Your Code Here"
IMPL_MARKER = "START IMPLEMENTATION"

# (file, role, one-line summary). Order is the reading order we suggest.
FILES: tuple[tuple[str, str, str], ...] = (
    ("instruction.py", "given",
     "Instruction formats as classes: memory, PE and full controller instructions, plus Mode."),
    ("processing_element.py", "graded",
     "One PE: two inputs, an accumulator and an output register. You implement the opcodes."),
    ("main_buffer.py", "graded",
     "MEM0, MEM1 and MEM2 with their ports. You implement READ and WRITE."),
    ("accelerator.py", "graded",
     "Top level: owns the main buffer and the PE array. You implement the controller."),
    ("assembler.py", "given",
     "Turns text like \"MAC INT16\" into instruction objects (bits)."),
    ("compiler.py", "given",
     "Turns a matrix-vector product into memory contents and assembly text."),
)

# Who owns or uses whom, for the "how it fits together" diagram.
OWNERSHIP: tuple[tuple[str, str, str], ...] = (
    ("Accelerator", "one MainBuffer", "owns"),
    ("Accelerator", "a list of PE_COUNT ProcessingElements", "owns"),
    ("Accelerator", "a list of Instructions", "runs"),
    ("Instruction", "a MemoryInstruction, a ProcessingElementInstruction, and Count / MemAIncrement / MemBIncrement", "contains"),
    ("MainBuffer", "MemoryInstructions", "executes"),
    ("ProcessingElement", "ProcessingElementInstructions", "executes"),
)

TEST_FLOW: tuple[tuple[str, str], ...] = (
    ("test_accelerator.py", "makes a random matrix and vector, and the numpy answer"),
    ("compiler.py", "packs them into MEM0/MEM1 contents and writes assembly text"),
    ("assembler.py", "turns the assembly text into Instruction objects"),
    ("Accelerator.execute_instructions", "loops over them, calling execute_instruction (yours)"),
    ("extract_results_from_memory", "reads MEM2 back out and compares with numpy"),
)


@dataclass(frozen=True)
class Concept:
    """A Python idiom, anchored to a real line of a given (ungraded) file."""

    title: str
    file: str
    find: str        # unique text on the anchor line
    before: int      # lines to include above the anchor
    after: int       # lines to include below the anchor
    explanation: str


CONCEPTS: tuple[Concept, ...] = (
    Concept("@dataclass: a class that is mostly fields", "instruction.py",
            "class MemoryInstructionConfiguration:", 1, 5,
            "@dataclass writes __init__ for you from the annotated fields. "
            "MemoryInstructionConfiguration(2, 2, 10, 10) sets the four fields in order; "
            "read them back as cfg.OPCODE_BITWIDTH. The configs for PEs, buffers and the "
            "accelerator all work this way."),
    Concept("Type hints", "instruction.py",
            "def set_mode(self, value : int) -> None:", 0, 0,
            "`value : int` says what the argument should be; `-> None` says the method "
            "returns nothing. Python does not enforce hints; they are documentation your "
            "editor can check."),
    Concept("self and _private names", "instruction.py",
            "self._memory_config = memory_config", 2, 0,
            "Methods receive the object as `self`; `self.x = ...` stores data on it. A leading "
            "underscore (_memory_config) means \"internal, don't touch from outside\" by "
            "convention only."),
    Concept("Class constants as an enum", "instruction.py",
            "class MemoryInstructionEnum:", 0, 3,
            "Plain class attributes used as named constants: write MemoryInstructionEnum.READ "
            "instead of a bare number. Below the class, `MI=MemoryInstructionEnum` is a "
            "shorter alias, so code writes MI.READ."),
    Concept("@staticmethod", "instruction.py",
            "def bitwidth(value : int) -> int:", 1, 1,
            "A function that lives on the class but needs no `self`. Call it as "
            "Mode.bitwidth(1)."),
    Concept("Building Bits", "instruction.py",
            "self._instruction_value = Bits(uint=0, length=self._memory_config.get_width())", 0, 0,
            "Bits(uint=..., length=n) makes an n-bit value from an unsigned number; "
            "Bits(int=..., length=n) from a signed one. It raises an error if the number "
            "doesn't fit."),
    Concept("Slicing Bits", "instruction.py",
            "return self._instruction_value[self._opcode_start:", 0, 0,
            "bits[a:b] takes bits a to b-1, counting from the LEFT (index 0 is the most "
            "significant bit). The result is a smaller Bits; .uint or .int reads it as a number."),
    Concept("Joining Bits", "instruction.py",
            "self._instruction_value = Bits().join([", 0, 5,
            "Bits().join([a, b, c]) glues pieces into one value, the first piece on the LEFT "
            "(most significant end)."),
    Concept(".cut, .int and a list comprehension", "compiler.py",
            "output = output + [elem.int for elem in value.cut(computation_bitwidth)]", 0, 0,
            "value.cut(n) yields n-bit pieces from left to right; elem.int reads each as signed. "
            "[expr for x in items] builds a list from a loop in one line."),
    Concept("_ as a throwaway loop variable", "compiler.py",
            "[Bits(int=0,length=config.BUFFER_CONFIG.MEM0_BITWIDTH) for _ in range(", 0, 0,
            "`for _ in range(n)` repeats n times when the loop variable isn't needed. The "
            "accelerator builds its PE array the same way."),
    Concept("Generic type hints", "compiler.py",
            ") -> tuple[AccelConfig, InstConfig]:", 0, 0,
            "tuple[A, B] means \"a pair of an A and a B\"; list[int] means \"a list of ints\". "
            "Returning a tuple lets a function hand back several values: "
            "accel_config, inst_config = generate_...()."),
    Concept("Relative imports", "assembler.py",
            "from .instruction import InstructionConfiguration", 0, 2,
            "The dot means \"from this same package\". That is why the tests import "
            "`src.assembler`: src is the package, and test/src is a link to it."),
    Concept("Raising errors with f-strings", "assembler.py",
            "raise ValueError(f\"Malformed Instruction: {inst_str}\")", 0, 0,
            "f\"...{x}...\" puts x's value into the string. `raise ValueError(...)` stops with "
            "an error message instead of continuing with bad data."),
)


# ------------------------------------------------------------------ parsing

def _method_status(source: str, node: ast.FunctionDef, graded: bool) -> str:
    if not graded:
        return "given"
    segment = ast.get_source_segment(source, node) or ""
    if TODO_MARKER in segment:
        return "todo"
    if IMPL_MARKER in segment:
        return "written"
    return "given"


def _comments(source: str, node: ast.FunctionDef) -> list[str]:
    """Comment lines inside a function, minus the course's marker lines."""
    segment = ast.get_source_segment(source, node) or ""
    out = []
    for line in segment.splitlines():
        text = line.strip()
        if text.startswith("#"):
            body = text.lstrip("#").strip()
            if body and IMPL_MARKER not in body and "END IMPLEMENTATION" not in body and TODO_MARKER not in body:
                out.append(body)
    return out


def _function(source: str, node: ast.FunctionDef, graded: bool) -> dict[str, Any]:
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    decorators = [ast.unparse(d) for d in node.decorator_list]
    return {
        "name": node.name,
        "line": node.lineno,
        "signature": f"{node.name}({ast.unparse(node.args)}){returns}",
        "decorators": decorators,
        "status": _method_status(source, node, graded),
        "comments": _comments(source, node),
        "docstring": ast.get_docstring(node),
    }


def parse_file(path: Path, role: str, summary: str = "") -> dict[str, Any]:
    """Describe one source file. A syntax error is reported, not raised."""
    graded = role == "graded"
    result: dict[str, Any] = {
        "name": path.name, "role": role, "summary": summary,
        "classes": [], "functions": [], "parse_error": None,
    }
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=path.name)
    except SyntaxError as err:
        result["parse_error"] = {"line": err.lineno, "message": err.msg}
        return result

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            result["classes"].append({
                "name": node.name,
                "line": node.lineno,
                "dataclass": any(ast.unparse(d) == "dataclass" for d in node.decorator_list),
                "fields": [
                    {"name": ast.unparse(s.target), "type": ast.unparse(s.annotation)}
                    for s in node.body if isinstance(s, ast.AnnAssign)
                ],
                "methods": [
                    _function(source, s, graded) for s in node.body if isinstance(s, ast.FunctionDef)
                ],
            })
        elif isinstance(node, ast.FunctionDef):
            result["functions"].append(_function(source, node, graded))
    return result


def resolve_concept(concept: Concept, src_dir: Path = SRC_DIR) -> dict[str, Any]:
    """Attach the real source lines for a concept, or ``snippet=None`` if not found."""
    data = asdict(concept)
    data.update({"line": None, "snippet": None})
    try:
        lines = (src_dir / concept.file).read_text(encoding="utf-8").splitlines()
    except OSError:
        return data
    for i, line in enumerate(lines):
        if concept.find in line:
            start = max(0, i - concept.before)
            data["line"] = i + 1
            data["snippet"] = "\n".join(lines[start:i + concept.after + 1])
            break
    del data["find"], data["before"], data["after"]
    return data


def starter_map(src_dir: Path = SRC_DIR) -> dict[str, Any]:
    """Everything the "Starter code" tab shows, read fresh from disk."""
    files = [parse_file(src_dir / name, role, summary) for name, role, summary in FILES]
    graded = [
        m for f in files if f["role"] == "graded"
        for c in f["classes"] for m in c["methods"] if m["status"] != "given"
    ]
    return {
        "files": files,
        "progress": {
            "written": sum(m["status"] == "written" for m in graded),
            "total": len(graded),
        },
        "ownership": [{"owner": a, "owned": b, "how": how} for a, b, how in OWNERSHIP],
        "test_flow": [{"step": s, "what": w} for s, w in TEST_FLOW],
        "concepts": [resolve_concept(c, src_dir) for c in CONCEPTS],
    }
