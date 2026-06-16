"""Smoke tests for the canonical APRT Reward Core package."""


def test_package_imports() -> None:
    import aprt

    assert aprt.__doc__
