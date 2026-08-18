"""Shared pytest configuration for source-mirrored tests."""


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: source-mirrored unit tests")
    config.addinivalue_line("markers", "integration: cross-module integration tests")
