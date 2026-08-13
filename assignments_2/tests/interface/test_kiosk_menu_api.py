from fastapi import status
from fastapi.testclient import TestClient
from src.interface.api.app import app

client = TestClient(app)


def test_get_menus_api_contains_tags_and_availability():
    """메뉴 목록 조회 시 tags 및 is_available 필드 검증"""
    response = client.get("/api/v1/menus")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first_menu = data[0]
    
    # 응답 스키마 필수 필드 존재 여부 검증
    assert "name" in first_menu
    assert "price" in first_menu
    assert "category" in first_menu
    assert "tags" in first_menu
    assert "is_available" in first_menu

    # 타입 검증
    assert isinstance(first_menu["tags"], list)
    assert isinstance(first_menu["is_available"], bool)