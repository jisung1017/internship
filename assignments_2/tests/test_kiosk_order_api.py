import uuid
import pytest


def test_create_order_success(client):
    """[정상 경로] 실제 스키마 기반 주문 생성 성공 및 응답 값 검증"""
    kiosk_uuid = str(uuid.uuid4())
    payload = {
        "items": [
            {
                "menu_name": "아메리카노",
                "quantity": 1,
                "selected_options": ["HOT"],
            }
        ]
    }

    response = client.post(
        "/api/v1/orders",
        json=payload,
        headers={"x-kiosk-uuid": kiosk_uuid},
    )

    assert response.status_code == 201
    data = response.json()
    assert "order_uuid" in data
    assert "total_price" in data
    assert data["client_uuid"] == kiosk_uuid
    assert response.headers.get("Location") == f"/api/v1/orders/{data['order_uuid']}"


def test_multiple_orders_same_kiosk(client):
    """[회귀 검증] 동일 x-kiosk-uuid로 연속 주문 시 서로 다른 order_uuid가 발급되어야 함"""
    kiosk_uuid = str(uuid.uuid4())
    payload = {
        "items": [
            {
                "menu_name": "아메리카노",
                "quantity": 1,
                "selected_options": ["HOT"],
            }
        ]
    }

    res1 = client.post(
        "/api/v1/orders",
        json=payload,
        headers={"x-kiosk-uuid": kiosk_uuid},
    )
    res2 = client.post(
        "/api/v1/orders",
        json=payload,
        headers={"x-kiosk-uuid": kiosk_uuid},
    )

    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res1.json()["order_uuid"] != res2.json()["order_uuid"]


def test_idempotent_order_submission(client):
    """[멱등성 검증] 동일한 Idempotency-Key 재요청 시 동일한 order_uuid를 반환해야 함"""
    kiosk_uuid = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    payload = {
        "items": [
            {
                "menu_name": "아메리카노",
                "quantity": 1,
                "selected_options": ["HOT"],
            }
        ]
    }
    headers = {
        "x-kiosk-uuid": kiosk_uuid,
        "Idempotency-Key": idempotency_key,
    }

    res1 = client.post("/api/v1/orders", json=payload, headers=headers)
    res2 = client.post("/api/v1/orders", json=payload, headers=headers)

    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res1.json()["order_uuid"] == res2.json()["order_uuid"]