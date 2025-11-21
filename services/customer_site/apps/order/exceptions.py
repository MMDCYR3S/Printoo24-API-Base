class OrderCreationError(Exception):
    pass

class EmptyCartError(OrderCreationError):
    pass

class InsufficientFundsError(OrderCreationError):
    pass