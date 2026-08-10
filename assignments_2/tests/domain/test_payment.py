import pytest
from unittest.mock import Mock

from src.domain.payment import Payment
from src.domain.exceptions import PaymentFailedError


class TestPaymentValidation:

    def test_payment_success(self):
        # Given: 결제가 승인되는 환경을 설정하고 가짜 주문 객체를 생성합니다.
        payment = Payment(is_approved=True)
        mock_order = Mock()

        # When & Then: pay 메서드가 예외 없이 정상적으로 실행되는지 검증합니다.
        try:
            payment.pay(mock_order)
        except PaymentFailedError:
            pytest.fail("결제가 성공하지않고 PaymentFailedError가 발생했습니다.")


    def test_payment_failed_raises_exception(self):
        # Given: 결제가 거절되는 환경을 설정하고 가짜 주문 객체를 생성합니다.
        payment = Payment(is_approved=False)
        mock_order = Mock()

        # When & Then: pay 메서드 호출 시 PaymentFailedError가 발생하는지 검증합니다.
        with pytest.raises(PaymentFailedError) as exc_info:
            payment.pay(mock_order)
        
        # 예외 메시지가 올바르게 출력되는지 확인합니다.
        assert str(exc_info.value) == "카드 승인 거절 또는 결제에 실패했습니다."
            