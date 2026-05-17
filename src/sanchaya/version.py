"""Version information for Sanchaya.

Centralizes version reporting so other modules import from one place.
"""

from sanchaya import __version__


def get_version() -> str:
    """Return the current Sanchaya version string.

    Returns:
        Semantic version string, e.g. "0.1.0".
    """
    return __version__
