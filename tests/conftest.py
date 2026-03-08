from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--run-long", action="store_true", default=False, help="Run long-running tests")
    parser.addoption("--reuse-recording", default=None, help="Path to existing recording dir, skip recording phase")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-long"):
        return
    skip = pytest.mark.skip(reason="needs --run-long to run")
    for item in items:
        if "long" in item.keywords:
            item.add_marker(skip)
