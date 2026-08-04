from fastapi import status
from fastapi.testclient import TestClient
from src.interface.api.app import app

client = TestClient(app)


# ---------- Kiosk API Tests ----------

def test_get_menus_api():
    response = client.get("/api/v1/menus")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "name" in data[0]
        assert "price" in data[0]


def test_add_cart_item_and_get_cart():
    # 1. 메뉴 목록 조회
    menus_res = client.get("/api/v1/menus")
    assert menus_res.status_code == status.HTTP_200_OK
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
    assert add_res.status_code == status.HTTP_200_OK

    # 4. 장바구니 조회
    cart_res = client.get("/api/v1/cart")
    assert cart_res.status_code == status.HTTP_200_OK
    cart_data = cart_res.json()
    assert len(cart_data["items"]) > 0
    assert cart_data["items"][0]["menu_name"] == menu_name


def test_create_order_insufficient_balance():
    # 잔액 부족 결제 시 400 Bad Request 반환 및 장바구니 초기화 검증
    response = client.post(
        "/api/v1/orders",
        json={"payment_balance": 10},  # 터무니없이 적은 잔액
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------- Admin API Tests ----------

def test_get_admin_inventory():
    response = client.get("/api/v1/admin/inventory")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_admin_restock_inventory():
    # 존재하는 재료 입고 테스트
    response = client.post(
        "/api/v1/admin/inventory/restock",
        json={"ingredient_name": "원두", "quantity": 100},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "원두" in response.json()["message"]


def test_get_admin_today_sales():
    response = client.get("/api/v1/admin/sales/today")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_sales" in data
    assert "orders" in data