import requests
from django.conf import settings
from django.db import transaction
from market.models import Payment, PAYMENT_STATUS_SUCCESS
from market.custom_exceptions import (
    PaymentNotFoundError,
    PaymentVerificationError
)
from market.serializers import PaymentVerifySerializer


class PaymentGatewayService:
    """hit the payment gateway's verify endpoint and return the response"""
    MERCHANT_ID = settings.MERCHANT_ID
    VERIFY_URL = settings.PAYMENT_VERIFY_GATEWAY

    @classmethod
    def payment_gateway_verify(cls, amount, authority):
        payload_data = {
            'merchant_id': cls.MERCHANT_ID,
            'amount': amount,
            'authority': authority
        }

        serializer = PaymentVerifySerializer(data=payload_data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        result = requests.post(
            url=cls.VERIFY_URL,
            json=payload,
            headers={
                'Accept': 'application/json',
                'Content-type': 'application/json'},
            timeout=10
        )

        return result.json()


class PaymentService:

    @transaction.atomic
    @staticmethod
    def verify_payment(authority):
        """check payment verification to update payment object afterwards"""

        # get the payment object
        payment = Payment.objects.filter(reference_id=authority).first()
        if not payment:
            raise PaymentNotFoundError

        # call payment gateway's verify endpoint
        amount = int(payment.order.total_price)
        result = PaymentGatewayService.payment_gateway_verify(
            amount=amount, authority=authority)

        # check the response
        if result.get('data', {}).get('message') != 'Verified':
            raise PaymentVerificationError(
                result.get('errors', 'Unknown error from gateway')
            )

        # update payment in db
        data = result['data']
        payment.status = PAYMENT_STATUS_SUCCESS
        payment.card_pan = data.get('card_pan')
        payment.transaction_id = data.get('ref_id')
        payment.fee = data.get('fee')
        payment.save()
