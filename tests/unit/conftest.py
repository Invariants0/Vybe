"""
Unit test configuration - uses PostgreSQL testcontainers like integration tests.
This ensures consistency across all test types.
"""
import pytest

# Unit tests will use the same PostgreSQL fixtures from parent conftest
# No need to override - they'll use the same testcontainer setup
