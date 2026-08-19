import uuid
import pytest

def test_create_order_success(client):
    """[정상 경로] 주문 생성 성공 시 201 응답 및 정상 데이터 반환 검증"""
    kiosk_uuid = str(uuid.uuid4())
    payload = {"items": [{"menu_id": 1, "quantity": 1, "options": []}]}
    
    response = client.post(
        "/api/v1/kiosk/orders",
        json=payload,
        headers={"x-kiosk-uuid": kiosk_uuid}
    )
    
    assert response.status_code == 201
    assert "id" in response.json()

def test_multiple_orders_same_kiosk(client):
    """[회귀 검증] 동일한 키오스크(x-kiosk-uuid)에서 연속 주문 시 정상적으로 2개의 주문이 생성되어야 함"""
    kiosk_uuid = str(uuid.uuid4())
    payload = {"items": [{"menu_id": 1, "quantity": 1, "options": []}]}
    
    res1 = client.post("/api/v1/kiosk/orders", json=payload, headers={"x-kiosk-uuid": kiosk_uuid})
    res2 = client.post("/api/v1/kiosk/orders", json=payload, headers={"x-kiosk-uuid": kiosk_uuid})
    
    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res1.json()["id"] != res2.json()["id"]  # 서로 다른 주문 ID여야 함

def test_idempotent_order_submission(client):
    """[멱등성 검증] 동일한 Idempotency-Key로 재요청 시 기존 주문을 반환해야 함"""
    kiosk_uuid = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    payload = {"items": [{"menu_id": 1, "quantity": 1, "options": []}]}
    headers = {
        "x-kiosk-uuid": kiosk_uuid,
        "Idempotency-Key": idempotency_key
    }
    
    res1 = client.post("/api/v1/kiosk/orders", json=payload, headers=headers)
    res2 = client.post("/api/v1/kiosk/orders", json=payload, headers=headers)
    
    assert res1.status_code == 201
    assert res2.status_code == 201
    assert res1.json()["id"] == res2.json()["id"]  # 동일한 주문 정보 반환