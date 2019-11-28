"""Routes involves user credentials"""
from flask import (
    abort,
    Blueprint,
    current_app,
    flash,
    redirect,
    request,
    render_template,
    session,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
)
from dropbox.oauth import (
    BadRequestException,
    BadStateException,
    CsrfException,
    NotApprovedException,
    ProviderException,
)
from .. import oauth
from ..forms import LoginForm, RegisterForm
from ..helper import (
    dropbox,
    pushover_required,
    youtube,
    youtube_required,
)
from ..models import User
user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """User Register"""
    if current_user.is_authenticated:
        flash("You've already logined!", "success")
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        exist_user = User.query.get(form.username.data)
        if not exist_user:
            new_user = User(form.username.data, form.password.data)
            current_app.db.session.add(new_user)
            current_app.db.session.commit()
            login_user(new_user)
            return redirect(url_for("main.dashboard"))
        flash("The Username is Taken", "warning")
    return render_template("register.html", form=form)


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """User Login"""
    if current_user.is_authenticated:
        flash("You've already logined!", "success")
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        query_user = User.query.get(form.username.data)
        if query_user and query_user.check_password(form.password.data):
            login_user(query_user)
            return redirect(url_for("main.dashboard"))
        flash("Invalid username or password.", "warning")
    return render_template("login.html", form=form)


@user_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    """User Logout"""
    logout_user()
    flash("You've Logged Out", "success")
    return redirect(url_for("user.login"))


@user_blueprint.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    """User Setting Page"""
    return render_template("setting.html")


@user_blueprint.route("/setting/youtube/authorize")
@login_required
def setting_youtube_authorize():
    flow = youtube.build_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true")
    session["state"] = state
    return redirect(authorization_url)


@user_blueprint.route("/setting/youtube/oauth_callback")
@login_required
def setting_youtube_oauth_callback():
    flow = youtube.build_flow(state=session["state"])
    flow.fetch_token(authorization_response=request.url)
    try:
        current_user.youtube = flow.credentials
    except (TypeError, ValueError) as error:
        flash("YouTube Access Failed: {}".format(error), "danger")
    else:
        flash("YouTube Access Granted", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.route("/setting/youtube/revoke")
@login_required
@youtube_required
def setting_youtube_revoke():
    if not current_user.youtube:
        flash("YouTube Credential isn't set", "warning")
    else:
        try:
            del current_user.youtube
        except ValueError as error:
            flash(str(error), "danger")
        else:
            flash("YouTube Access Revoke", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.route("/setting/line-notify/authorize")
@login_required
def setting_line_notify_authorize():
    redirect_uri = url_for("user.setting_line_notify_oauth_callback",
                           _external=True)
    return oauth.LineNotify.authorize_redirect(redirect_uri)


@user_blueprint.route("/setting/line-notify/oauth_callback")
@login_required
def setting_line_notify_oauth_callback():
    token = oauth.LineNotify.authorize_access_token()
    current_user.line_notify = token["access_token"]
    flash("Line Notify Access Granted", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.route("/setting/line-notify/revoke")
@login_required
def setting_line_notify_revoke():
    """Revoke User's Line Notify Crendential"""
    if not current_user.line_notify_credentials:
        flash("Line Notify Credential isn't set", "warning")
    else:
        try:
            del current_user.line_notify
        except RuntimeError as error:
            flash(str(error), "danger")
        else:
            flash("Line Notify Access Revoke", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.route("/setting/dropbox/authorize")
@login_required
def setting_dropbox_authorize():
    authorize_url = dropbox.build_flow(session).start()
    return redirect(authorize_url)


@user_blueprint.route("/setting/dropbox/oauth_callback")
@login_required
def setting_dropbox_oauth_callback():
    try:
        oauth_result = dropbox.build_flow(session).finish(request.args)
    except BadRequestException as error:
        abort(400)
    except BadStateException as error:
        # Session Expire, Start the auth flow again.
        return redirect(url_for("user.setting"))
    except CsrfException as error:
        # CSRF Not Matched, Raise Error
        abort(403)
    except NotApprovedException as error:
        # User didn't Grant Access
        return redirect(url_for("user.setting"))
    except ProviderException as error:
        # I Have no clue of what this is for...?
        abort(403)
    current_user.dropbox = {
        "access_token": oauth_result.access_token,
        "account_id": oauth_result.account_id,
        "user_id": oauth_result.user_id,
        "url_state": oauth_result.url_state
    }
    flash("Dropbx Access Granted", "success")
    return redirect(url_for("user.setting"))


@user_blueprint.route("/setting/dropbox/revoke")
@login_required
def setting_dropbox_revoke():
    """Revoke User's Dropbx Crendential"""
    if not current_user.dropbox:
        flash("Dropbx Credential isn't set", "warning")
    else:
        try:
            del current_user.dropbox
            flash("Dropbx Access Revoke", "success")
        except Exception as error:
            flash("{}: {}".format(type(error), error), "danger")
    return redirect(url_for("user.setting"))
