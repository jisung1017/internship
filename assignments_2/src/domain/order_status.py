from enum import Enum


class OrderStatus(str, Enum):
    ORDERED = "ORDERED"    # 주문 접수 / 제조 대기
    COMPLETE = "COMPLETE"  # 제조 완료 / 제공 완료
    CANCEL = "CANCEL"      # 주문 취소 (종결 상태)