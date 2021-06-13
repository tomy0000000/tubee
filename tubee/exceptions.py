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

    def __init__(self, service: str, message: str, error_type: str = "", *args):
        type_string = f"<{error_type}> " if error_type else ""
        super().__init__(f"Error from {service}: {type_string}{message}", *args)


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
