"""Starter-code map: parses files, tracks graded-method progress, survives
syntax errors, and every Python concept points at a real line."""

from pathlib import Path

import pytest

from viz.starter import CONCEPTS, SRC_DIR, parse_file, resolve_concept, starter_map

GRADED_SAMPLE = '''
from dataclasses import dataclass

@dataclass
class Cfg:
    WIDTH : int

def helper(x: int) -> int:
    return x

class Thing:
    def todo_method(self) -> None:
        # START IMPLEMENTATION
        # Your Code Here
        # END IMPLEMENTATION
        return None

    def done_method(self) -> None:
        # Clamp each lane.
        # START IMPLEMENTATION
        self.x = 1
        # END IMPLEMENTATION
        return None

    def given_method(self) -> int:
        return 3
'''


@pytest.fixture
def graded_file(tmp_path: Path) -> Path:
    path = tmp_path / "thing.py"
    path.write_text(GRADED_SAMPLE)
    return path


def test_graded_status_tracks_the_marker(graded_file: Path) -> None:
    info = parse_file(graded_file, "graded")
    methods = {m["name"]: m for m in info["classes"][1]["methods"]}
    assert methods["todo_method"]["status"] == "todo"
    assert methods["done_method"]["status"] == "written"
    assert methods["given_method"]["status"] == "given"


def test_comments_keep_hints_but_drop_markers(graded_file: Path) -> None:
    info = parse_file(graded_file, "graded")
    done = info["classes"][1]["methods"][1]
    assert done["comments"] == ["Clamp each lane."]


def test_dataclass_fields_and_functions(graded_file: Path) -> None:
    info = parse_file(graded_file, "graded")
    cfg = info["classes"][0]
    assert cfg["dataclass"] is True
    assert cfg["fields"] == [{"name": "WIDTH", "type": "int"}]
    assert info["functions"][0]["signature"] == "helper(x: int) -> int"


def test_given_files_never_report_todo(graded_file: Path) -> None:
    info = parse_file(graded_file, "given")
    assert {m["status"] for c in info["classes"] for m in c["methods"]} == {"given"}


def test_syntax_error_is_reported_with_line(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def f(:\n    pass\n")
    info = parse_file(bad, "graded")
    assert info["parse_error"]["line"] == 1
    assert info["classes"] == []


@pytest.mark.parametrize("concept", CONCEPTS, ids=[c.title for c in CONCEPTS])
def test_every_concept_points_at_a_real_line(concept) -> None:
    data = resolve_concept(concept)
    assert data["snippet"] is not None, f"{concept.find!r} not found in {concept.file}"
    assert concept.find in data["snippet"]


def test_concepts_only_use_ungraded_files() -> None:
    # Graded files change as the student works; anchors there would break.
    assert {c.file for c in CONCEPTS} <= {"instruction.py", "compiler.py", "assembler.py"}


def test_map_lists_all_starter_files() -> None:
    data = starter_map()
    assert [f["name"] for f in data["files"]] == [
        "instruction.py", "processing_element.py", "main_buffer.py",
        "accelerator.py", "assembler.py", "compiler.py",
    ]
    assert all((SRC_DIR / f["name"]).is_file() for f in data["files"])
    assert data["progress"]["total"] >= data["progress"]["written"] >= 0
