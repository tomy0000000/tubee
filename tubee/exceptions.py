"""Exceptions used in this module"""


class TubeeError(Exception):
    """Base class for exception related to Tubee

    Extends:
        Exception
    """

    def __init__(self, description):
        """Constructor

        Arguments:
            description {str} -- The error description
        """
        self.description = description


class UserError(TubeeError):
    """Base class for exception raised by user's invalid action or input

    Extends:
        TubeeError
    """

    def __init__(self, description):
        super().__init__(description)


class APIError(TubeeError):
    """Upstream API Error that

    Extends:
        TubeeError
    """

    def __init__(self, service: str, message: str, error_type: str = ""):
        type_string = f"<{error_type}> " if error_type else ""
        super().__init__(f"Error from {service}: {type_string}{message}")


class InvalidAction(UserError):
    """Raised when user filled in invalid parameter

    Extends:
        UserError
    """

    def __init__(self, description):
        super().__init__(description)


class ServiceNotAuth(UserError):
    """Raised when user attempt to do something that require service to be setup first

    Extends:
        UserError
    """

    def __init__(self, service):
        super().__init__(f"{service} has not authenticated yet.")
