"""Tests for `eazyapi` module."""
from typing import Generator

import pytest

import eazyapi

__version__ = "0.1.1"


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield eazyapi.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == __version__
