"""
Unit test configuration - no database fixtures needed.
Unit tests should use mocks instead of real database.
"""
import pytest

# Override the clean_database fixture from parent conftest to do nothing for unit tests
@pytest.fixture(autouse=True)
def clean_database():
    """No-op for unit tests - they should use mocks."""
    pass
