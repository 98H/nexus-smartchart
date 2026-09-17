"""
Unit tests for the core 'smartchart' package initialization and versioning.

Acceptance Criteria:
- Given a newly initialized Python monorepo environment
- When the `smartchart` package is imported
- Then the package should expose a valid `__version__` string and be identifiable
  as the core module.
"""

from __future__ import annotations

import re
import types
from pathlib import Path

import pytest

# PEP 440 & Semantic Versioning compliant regex
SEMVER_PEP440_REGEX = re.compile(
    r"^"
    r"(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:(?P<prerelease>(?:a|b|rc|alpha|beta|dev)\d*|\-(?:[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
    r"$"
)


def test_smartchart_package_can_be_imported():
    """Verify that the smartchart package is importable and is a module."""
    import smartchart

    assert isinstance(smartchart, types.ModuleType), "smartchart should be an imported module"
    assert smartchart.__name__ == "smartchart", "Module __name__ must be 'smartchart'"


def test_smartchart_package_location_and_structure():
    """Verify smartchart is identifiable as a top-level package with an __init__.py file."""
    import smartchart

    assert hasattr(smartchart, "__file__"), "smartchart package must have a '__file__' attribute"
    assert smartchart.__file__ is not None, "smartchart.__file__ must not be None"

    init_path = Path(smartchart.__file__)
    assert init_path.name == "__init__.py", "smartchart root must be defined by an __init__.py"
    assert init_path.parent.name == "smartchart", "Containing directory must be named 'smartchart'"


def test_version_module_import():
    """Verify that smartchart.version exists and can be imported directly."""
    import smartchart.version

    assert isinstance(
        smartchart.version, types.ModuleType
    ), "smartchart.version must be a valid module"
    assert hasattr(
        smartchart.version, "__version__"
    ), "smartchart.version must define '__version__'"


def test_smartchart_exposes_version_attribute():
    """Verify that the top-level package exposes '__version__' as a non-empty string."""
    import smartchart

    assert hasattr(smartchart, "__version__"), "smartchart package must expose '__version__'"
    assert isinstance(
        smartchart.__version__, str
    ), f"Expected __version__ to be a string, got {type(smartchart.__version__).__name__}"
    assert smartchart.__version__.strip() != "", "__version__ must not be an empty string"


def test_smartchart_version_format_is_valid():
    """Verify that smartchart.__version__ conforms to standard SemVer / PEP 440 formats."""
    import smartchart

    version_str = smartchart.__version__
    match = SEMVER_PEP440_REGEX.match(version_str)
    assert match is not None, (
        f"Version string '{version_str}' does not conform to PEP 440 / SemVer specifications "
        f"(e.g., '0.1.0', '1.0.0-rc1', '0.1.0.dev0')."
    )


def test_smartchart_version_consistency():
    """Verify that smartchart.__version__ matches smartchart.version.__version__ identically."""
    import smartchart
    import smartchart.version

    assert smartchart.__version__ == smartchart.version.__version__, (
        f"Mismatch between smartchart.__version__ ({smartchart.__version__}) "
        f"and smartchart.version.__version__ ({smartchart.version.__version__})"
    )


def test_smartchart_dunder_all_exports_version():
    """If __all__ is declared, ensure '__version__' is explicitly exported."""
    import smartchart

    if hasattr(smartchart, "__all__"):
        assert "__version__" in smartchart.__all__, (
            "smartchart.__all__ is defined but does not include '__version__'"
        )


def test_smartchart_is_not_empty_namespace():
    """Ensure smartchart has package attributes and is not an uninitialized empty namespace."""
    import smartchart

    assert hasattr(smartchart, "__path__"), "smartchart must be a package containing a '__path__'"
    assert len(smartchart.__path__) > 0, "smartchart.__path__ must not be empty"