from fastapi.testclient import TestClient
from src.interface.api.app import app

client = TestClient(app)


def test_get_menus_api():
    response = client.get("/api/v1/menus")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "name" in data[0]
        assert "price" in data[0]


def test_add_cart_item_and_get_cart():
    # 1. 메뉴 목록 조회
    menus_res = client.get("/api/v1/menus")
    assert menus_res.status_code == 200
    menus_data = menus_res.json()
    assert len(menus_data) > 0

    target_menu = menus_data[0]
    menu_name = target_menu["name"]

    # 2. 필수 옵션 그룹에서 첫 번째 옵션들 선택
    selected_options = []
    for group in target_menu.get("option_groups", []):
        if group.get("options") and group.get("min_quantity", 0) > 0:
            selected_options.append(group["options"][0]["name"])

    # 3. 장바구니 항목 추가
    add_res = client.post(
        "/api/v1/cart/items",
        json={
            "menu_name": menu_name,
            "quantity": 1,
            "selected_options": selected_options,
        },
    )
    assert add_res.status_code == 200

    # 4. 장바구니 조회
    cart_res = client.get("/api/v1/cart")
    assert cart_res.status_code == 200
    cart_data = cart_res.json()
    assert len(cart_data["items"]) > 0
    assert cart_data["items"][0]["menu_name"] == menu_name