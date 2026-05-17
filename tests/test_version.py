"""Tests for sanchaya.version module."""

from sanchaya.version import get_version


def test_get_version_returns_string() -> None:
    """get_version() must return a non-empty string."""
    version = get_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_get_version_is_semver() -> None:
    """Version should follow semver: MAJOR.MINOR.PATCH."""
    version = get_version()
    parts = version.split(".")
    assert len(parts) == 3, f"Expected 3 parts (MAJOR.MINOR.PATCH), got {parts}"
    for part in parts:
        assert part.isdigit(), f"Each version part must be a number, got {part}"
