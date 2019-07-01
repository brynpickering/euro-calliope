import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--include-regional-resolution",
        action="store_true",
        default=False,
        help="run tests on the regional resolution"
    )
    parser.addoption(
        "--test-scaling",
        action="store_true",
        default=False,
        help="run scaling test"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "regional: mark test as running on regional resolution")
    config.addinivalue_line("markers", "scaling: mark test as testing scaling")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--include-regional-resolution"):
        skip_regional = pytest.mark.skip(reason="Use command line flag to run on regional resolution.")
        for item in items:
            if "regional" in item.keywords:
                item.add_marker(skip_regional)
    if not config.getoption("--test-scaling"):
        skip_scaling = pytest.mark.skip(reason="Use command line flag to run scaling tests.")
        for item in items:
            if "scaling" in item.keywords:
                item.add_marker(skip_scaling)
