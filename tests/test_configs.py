"""Lane geometry and presets. Expected values come straight from the spec
(section 3.1: "four 16-bit accumulator lanes in INT8, two 32-bit lanes in
INT16, or one 64-bit lane in INT32")."""

import pytest

from viz.configs import PRESETS, UnknownPresetError, lane_geometry, preset_config


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        (8, {"lanes": 4, "input_lane_bits": 8, "acc_lane_bits": 16, "output_lane_bits": 8}),
        (16, {"lanes": 2, "input_lane_bits": 16, "acc_lane_bits": 32, "output_lane_bits": 16}),
        (32, {"lanes": 1, "input_lane_bits": 32, "acc_lane_bits": 64, "output_lane_bits": 32}),
    ],
)
def test_lane_geometry_matches_spec(mode: int, expected: dict[str, int]) -> None:
    assert lane_geometry(32, 64, 32, mode) == expected


def test_lane_geometry_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="mode"):
        lane_geometry(32, 64, 32, 4)


@pytest.mark.parametrize("name", list(PRESETS))
def test_presets_build_valid_course_configs(name: str) -> None:
    cfg = preset_config(name)
    assert cfg["pe_count"] == PRESETS[name].pe_count
    assert cfg["memories"]["mem0"]["bitwidth"] == cfg["pe_count"] * cfg["pe"]["input_bitwidth"]
    assert cfg["memories"]["mem2"]["bitwidth"] == cfg["pe_count"] * cfg["pe"]["output_bitwidth"]
    assert set(cfg["modes"]) == {"8", "16", "32"}


def test_unknown_preset_raises() -> None:
    with pytest.raises(UnknownPresetError):
        preset_config("no-such-preset")
