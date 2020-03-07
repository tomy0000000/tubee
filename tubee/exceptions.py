"""Exceptions used in this module"""


class TubeeError(Exception):
    """Base Class used to declare other errors for Tubee

    Extends:
        Exception
    """
    pass


class UserError(TubeeError):
    """Base Class for errors related to user

    Extends:
        TubeeError
    """
    pass


class BackendError(TubeeError):
    """Base Class for errors happening in the background

    Extends:
        TubeeError
    """
    pass


class InvalidParameter(UserError):
    """Raised when user filled in invalid parameter

    Extends:
        UserError
    """
    pass


class ServiceNotSet(UserError):
    """Raised when user attempt to do something that require service to be setup first

    Extends:
        UserError
    """
    pass


# class SubscriptionNotFound(UserError):
#     """Raised when user attempt to make interaction with subscription that doesn't exists

#     Extends:
#         UserError
#     """
#     pass
