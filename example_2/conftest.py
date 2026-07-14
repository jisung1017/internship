import pytest

from example_2.interfaces.domain.menu import Menu


@pytest.fixture
def test_menu():
    return Menu(
        id=1,
        name="아메리카노",
        price=3000,
        description="맛있는 아메리카노",
    )
