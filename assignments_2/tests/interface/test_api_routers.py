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


def test_get_menus():
    menus_res = client.get("/api/v1/menus")
    assert menus_res.status_code == status.HTTP_200_OK
    menus_data = menus_res.json()
    assert len(menus_data) > 0


def test_create_order_insufficient_balance():
    # 잔액 부족 결제 시 400 Bad Request 반환 및 장바구니 초기화 검증
    response = client.post(
        "/api/v1/orders",
        json={"payment_balance": 10},  # 터무니없이 적은 잔액
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


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