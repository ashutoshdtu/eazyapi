"""Tests for `eazyapi` module."""
from typing import Generator

import pytest
import toml

import eazyapi


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield eazyapi.__version__


def test_version(version: str) -> None:
    """Test whether version in eazyapi.__version__ is the same as in pyproject.toml."""
    # Load the pyproject.toml file
    pyproject = toml.load("pyproject.toml")

    # Get the version number from the [tool.poetry] section
    expected_version = pyproject["tool"]["poetry"]["version"]

    assert version == expected_version
