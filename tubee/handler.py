"""Error Handlers"""
import traceback
from flask import (
    Blueprint,
    flash,
    jsonify,
    render_template,
    request,
)
from flask_login import current_user
from werkzeug.exceptions import HTTPException
handler = Blueprint("handler", __name__)


@handler.app_errorhandler(Exception)
def unhandled_exception(error):
    """
    400 <BadRequest>                    :
    401 <Unauthorized>                  : Raised when User didn't logined yet
    403 <Forbidden>                     : Raised when User did login, but didn't had the permission
    404 <NotFound>                      : Raised when page can not be found
    405 <MethodNotAllowed>              : Raised when endpoint is visited with wrong method
    406 <NotAcceptable>                 : Raised when response content doesn't fit headers requirement
    408 <RequestTimeout>                :
    409 <Conflict>                      :
    410 <Gone>                          :
    411 <LengthRequired>                :
    412 <PreconditionFailed>            :
    413 <RequestEntityTooLarge>         :
    414 <RequestURITooLarge>            :
    415 <UnsupportedMediaType>          :
    416 <RequestedRangeNotSatisfiable>  :
    417 <ExpectationFailed>             :
    418 <ImATeapot>                     :
    422 <UnprocessableEntity>           :
    423 <Locked>                        :
    424 <FailedDependency>              :
    428 <PreconditionRequired>          :
    429 <TooManyRequests>               :
    431 <RequestHeaderFieldsTooLarge>   :
    451 <UnavailableForLegalReasons>    :
    500 <InternalServerError>           : Raised when something went wrong unexpectedly
    501 <NotImplemented>                : Raised when the endpoint is not implemented yet
    502 <BadGateway>                    :
    503 <ServiceUnavailable>            :
    504 <GatewayTimeout>                :
    505 <HTTPVersionNotSupported>       :
    https://werkzeug.palletsprojects.com/en/1.0.x/exceptions/#error-classes
    """

    # Log error to traceback if error is not triggered intentionally
    if isinstance(error, HTTPException):
        code = error.code
    else:
        try:
            raise error
        except Exception:
            pass
        traceback.print_exc()
        code = 500

    # Return an error response to user
    if request.path.startswith("/api"):
        return jsonify({"code": code, "description": str(error)}), code
    if current_user.is_authenticated and current_user.admin:
        flash(traceback.format_exc(), "danger")
    else:
        flash(error, "danger")
    return render_template("error.html"), code
