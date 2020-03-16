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


class DatabaseError(TubeeError):
    """Base Class for errors related to database

    Extends:
        TubeeError
    """
    pass


class APIError(TubeeError):
    """Base Class for errors related to APIs

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


class OperationalError(DatabaseError):
    """Raised when attempt to execute operation that is not permitted

    Extends:
        DatabaseError
    """

# class SubscriptionNotFound(UserError):
#     """Raised when user attempt to make interaction with subscription that doesn't exists

#     Extends:
#         UserError
#     """
#     pass
