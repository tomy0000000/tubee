"""Exceptions used in this module"""


class TubeeError(Exception):
    """Base class for exception related to Tubee

    Extends:
        Exception
    """

    pass


class UserError(TubeeError):
    """Base class for exception raised by user's invalid action or input

    Extends:
        TubeeError
    """

    pass


class APIError(TubeeError):
    """Base Class for errors related to APIs

    Extends:
        TubeeError
    """

    def __init__(self, service, message, *args, error_type: str = None):
        if isinstance(error_type, str):
            error_type += " "
        super().__init__(f"Error <{error_type}> from {service}: {message}")


class InvalidAction(UserError, ValueError):
    """Raised when user filled in invalid parameter

    Extends:
        UserError
    """

    pass


class ServiceNotAuth(UserError):
    """Raised when user attempt to do something that require service to be setup first

    Extends:
        UserError
    """

    def __init__(self, service, *args):
        super().__init__(f"{service} has not authenticated yet.")
