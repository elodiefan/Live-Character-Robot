"""Tests for portable measurement calculation and persistence."""

import json

import pytest

from live_character_robot.measurements import peak_memory_mb, write_results


def test_peak_memory_normalizes_macos_bytes() -> None:
    """macOS reports maximum resident size in bytes."""
    assert peak_memory_mb(104857600, "Darwin") == 100.0


def test_peak_memory_normalizes_linux_kibibytes() -> None:
    """Linux reports maximum resident size in KiB."""
    assert peak_memory_mb(102400, "Linux") == 100.0


def test_write_results_creates_json_parent(
    tmp_path: pytest.TempPathFactory,
) -> None:
    """Measurement evidence should be reproducible and machine-readable."""
    output = tmp_path / "nested" / "results.json"

    write_results(output, {"latency": 1.25})

    assert json.loads(output.read_text()) == {"latency": 1.25}
