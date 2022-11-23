"""Routes involves user credentials"""
from dropbox.oauth import (
    BadRequestException,
    BadStateException,
    CsrfException,
    NotApprovedException,
    ProviderException,
)
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user  # type: ignore
from flask_login import login_required, login_user, logout_user

from .. import oauth
from ..forms import UserForm
from ..models import User
from ..utils import dropbox, is_safe_url, youtube

current_user: User

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """User Register"""
    if current_user.is_authenticated:
        flash("You've already logined!", "success")
        return redirect(url_for("main.dashboard"))
    form = UserForm(submit_label="Register", password_confirm=True)
    if form.validate_on_submit():
        exist_user = User.query.get(form.username.data)
        if not exist_user:
            new_user = User(form.username.data, form.password.data)
            login_user(new_user)
            return redirect(url_for("main.dashboard"))
        flash("The Username is Taken", "warning")
    return render_template("user/register.html", form=form)


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """User Login"""
    if current_user.is_authenticated:
        flash("You've already logined!", "success")
        return redirect(url_for("main.dashboard"))
    form = UserForm(submit_label="Login", password_confirm=False)
    if form.is_submitted():
        if form.validate():
            query_user = User.query.get(form.username.data)
            if query_user and query_user.check_password(form.password.data):
                login_user(query_user, remember=True)
                redirect_url = request.args.get("next")
                if redirect_url and is_safe_url(redirect_url):
                    return redirect(redirect_url)
                return redirect(url_for("main.dashboard"))
        flash("Invalid username or password.", "warning")
    return render_template("user/login.html", form=form)


@user_blueprint.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change Password"""
    form = UserForm(
        username=current_user.username, submit_label="Save", password_confirm=True
    )
    if form.validate_on_submit():
        current_user.password = form.password.data
        flash("Password Changed", "success")
        return redirect(url_for("user.setting"))
    return render_template("user/change_password.html", form=form)


@user_blueprint.get("/logout")
@login_required
def logout():
    """User Logout"""
    logout_user()
    flash("You've Logged Out", "success")
    return redirect(url_for("user.login"))


@user_blueprint.get("/setting")
@login_required
def setting():
    """User Setting Page"""
    return render_template("user/setting.html")


@user_blueprint.get("/setting/youtube/authorize")
@login_required
def setting_youtube_authorize():
    flow = youtube.build_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(authorization_url)


@user_blueprint.post("/setting/pushover")
@login_required
def pushover():
    user_key = request.form.get("pushover")
    if user_key:
        current_user.pushover = user_key
        flash("Pushover user key validate and saved", "success")
    else:
        del current_user.pushover
        flash("Pushover user key deleted", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.get("/setting/youtube/oauth_callback")
@login_required
def setting_youtube_oauth_callback():
    flow = youtube.build_flow(state=session["state"])
    flow.fetch_token(authorization_response=request.url)
    try:
        current_user.youtube = flow.credentials
    except (TypeError, ValueError) as error:
        flash(f"YouTube Access Failed: {error}", "danger")
    else:
        flash("YouTube Access Granted", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.get("/setting/youtube/revoke")
@login_required
def setting_youtube_revoke():
    del current_user.youtube
    flash("YouTube Access Revoked", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.get("/setting/line-notify/authorize")
@login_required
def setting_line_notify_authorize():
    redirect_uri = url_for("user.setting_line_notify_oauth_callback", _external=True)
    return oauth.LineNotify.authorize_redirect(redirect_uri)  # type: ignore


@user_blueprint.get("/setting/line-notify/oauth_callback")
@login_required
def setting_line_notify_oauth_callback():
    token = oauth.LineNotify.authorize_access_token()  # type: ignore
    current_user.line_notify = token["access_token"]
    flash("Line Notify Access Granted", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.get("/setting/line-notify/revoke")
@login_required
def setting_line_notify_revoke():
    """Revoke User's Line Notify Crendential"""
    try:
        del current_user.line_notify
    except RuntimeError as error:
        flash(str(error), "danger")
    else:
        flash("Line Notify Access Revoke", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.get("/setting/dropbox/authorize")
@login_required
def setting_dropbox_authorize():
    authorize_url = dropbox.build_flow(session).start()
    return redirect(authorize_url)


@user_blueprint.get("/setting/dropbox/oauth_callback")
@login_required
def setting_dropbox_oauth_callback():
    try:
        oauth_result = dropbox.build_flow(session).finish(request.args)
    except BadRequestException:
        abort(400)
    except BadStateException:
        # Session Expire, Start the auth flow again.
        return redirect(url_for("user.setting"))
    except CsrfException:
        # CSRF Not Matched, Raise Error
        abort(403)
    except NotApprovedException:
        # User didn't Grant Access
        return redirect(url_for("user.setting"))
    except ProviderException:
        # I Have no clue of what this is for...?
        abort(403)
    current_user.dropbox = oauth_result
    flash("Dropbx Access Granted", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.get("/setting/dropbox/revoke")
@login_required
def setting_dropbox_revoke():
    """Revoke User's Dropbx Crendential"""
    del current_user.dropbox
    flash("Dropbx Access Revoke", "success")
    return redirect(url_for("user.setting"))
