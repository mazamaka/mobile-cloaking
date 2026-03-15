"""Semantic version comparison utilities."""


def parse_version(v: str) -> tuple[int, ...]:
    """Parse version string into tuple of integers.

    Handles formats: "1.0", "1.0.0", "2.1.3.4"
    Non-numeric parts are treated as 0.
    """
    parts: list[int] = []
    for part in v.strip().split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def version_lt(a: str, b: str) -> bool:
    """Check if version a < version b (semver comparison)."""
    return parse_version(a) < parse_version(b)


def check_update(
    app_version: str,
    min_version: str | None,
    latest_version: str | None,
) -> str | None:
    """Determine update mode based on version comparison.

    Returns:
        "force" if app_version < min_version
        "soft" if app_version < latest_version
        None if no update needed
    """
    if min_version and version_lt(app_version, min_version):
        return "force"
    if latest_version and version_lt(app_version, latest_version):
        return "soft"
    return None
