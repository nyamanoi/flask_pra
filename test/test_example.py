import pytest


def test_add():
    assert 1 + 1 == 2


def test_subtraction():
    assert 3 - 1 == 2


@pytest.fixture
def sample_data():
    return {"key": "value"}


def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"


@pytest.mark.parametrize(
    "input1, input2, expected",
    [
        (1, 2, 3),
        (2, 3, 6),
        (3, 5, 8),
    ],
)
def test_addition(input1, input2, expected):
    assert input1 + input2 == expected
