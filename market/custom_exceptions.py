class OrderItemCannotConfirmError(Exception):
    pass


class OutOfStockError(Exception):
    pass


class PaymentNotFoundError(Exception):
    pass


class PaymentVerificationError(Exception):
    pass
