from fastapi import status


# ---------- Kiosk API Tests ----------

def test_get_menus_api(client):
    response = client.get("/api/v1/menus")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "아메리카노"


def test_get_menus(client):
    menus_res = client.get("/api/v1/menus")
    assert menus_res.status_code == status.HTTP_200_OK
    menus_data = menus_res.json()
    assert len(menus_data) == 1


def test_create_order_insufficient_balance(client):
    response = client.post(
        "/api/v1/orders",
        json={"payment_balance": 10},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ---------- Admin API Tests ----------

def test_get_admin_inventory(client):
    response = client.get("/api/v1/admin/inventory")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_admin_restock_inventory(client):
    response = client.post(
        "/api/v1/admin/inventory/restock",
        json={"ingredient_name": "원두", "quantity": 100},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "원두 100개 입고 완료" in response.json()["message"]


def test_get_admin_today_sales(client):
    response = client.get("/api/v1/admin/sales/today")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_sales" in data
    assert "orders" in data


def test_get_admin_inventory_history(client):
    """재고 변동 이력 조회 기능 검증"""
    # 1. 입고 수행하여 이력 발생
    client.post(
        "/api/v1/admin/inventory/restock",
        json={"ingredient_name": "원두", "quantity": 100},
    )

    # 2. 이력 목록 조회
    response = client.get("/api/v1/admin/inventory/history")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["ingredient_name"] == "원두"
    assert data[0]["change"] == 100
    assert data[0]["reason"] == "RESTOCK"