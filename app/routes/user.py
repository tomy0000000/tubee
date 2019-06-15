"""Routes involves user credentials"""
from flask import abort, Blueprint, current_app, redirect, request, render_template, session, url_for
from flask_login import current_user, login_user, logout_user, login_required
from dropbox.oauth import BadRequestException, BadStateException, CsrfException, NotApprovedException, ProviderException
from .. import oauth
from ..forms import LoginForm, RegisterForm
from ..helper import dropbox, youtube
from ..models import User
user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """User Register"""
    if current_user.is_authenticated:
        session["alert"] = "You've already logined!"
        session["alert_type"] = "success"
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    alert = None
    if form.validate_on_submit():
        query_user = User.query.filter_by(username=form.username.data).first()
        if not query_user:
            new_user = User(form.username.data, form.password.data)
            current_app.db.session.add(new_user)
            current_app.db.session.commit()
            login_user(new_user)
            return redirect(url_for("main.dashboard"))
        alert = "The Username is Taken"
    return render_template("register.html",
                           form=form,
                           alert=alert,
                           alert_type="warning")

@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """User Login"""
    if current_user.is_authenticated:
        session["alert"] = "You've already logined!"
        session["alert_type"] = "success"
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    alert = session.pop("login_message_body", None)
    alert_type = session.pop("login_message_type", None)
    if form.validate_on_submit():
        query_user = User.query.filter_by(username=form.username.data).first()
        if query_user and query_user.check_password(form.password.data):
            login_user(query_user)
            return redirect(url_for("main.dashboard"))
        alert = "Invalid username or password."
        alert_type = "warning"
    return render_template("login.html",
                           form=form,
                           alert=alert,
                           alert_type=alert_type)

@user_blueprint.route("/logout", methods=["GET"])
@login_required
def logout():
    """User Logout"""
    logout_user()
    session["login_message_body"] = "You've Logged Out"
    session["login_message_type"] = "success"
    return redirect(url_for("user.login"))

@user_blueprint.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    """User Setting Page"""
    alert = session.pop("alert", None)
    alert_type = session.pop("alert_type", None)
    return render_template("setting.html",
                           alert=alert,
                           alert_type=alert_type)

@user_blueprint.route('/setting/youtube/authorize')
@login_required
def setting_youtube_authorize():
    flow = youtube.build_flow()
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true")
    session["state"] = state
    return redirect(authorization_url)

@user_blueprint.route("/setting/youtube/oauth_callback")
@login_required
def setting_youtube_oauth_callback():
    flow = youtube.build_flow(state=session["state"])
    flow.fetch_token(authorization_response=request.url)
    credentials_dict = {
        "token": flow.credentials.token,
        "refresh_token": flow.credentials.refresh_token,
        "token_uri": flow.credentials.token_uri,
        "client_id": flow.credentials.client_id,
        "client_secret": flow.credentials.client_secret,
        "scopes": flow.credentials.scopes
    }
    current_user.youtube_init(credentials_dict)
    if flow.credentials.valid:
        session["alert"] = "YouTube Access Granted"
        session["alert_type"] = "success"
    else:
        session["alert"] = "YouTube Access Failed"
        session["alert_type"] = "danger"
    return redirect(url_for("user.setting"))

@user_blueprint.route("/setting/youtube/revoke")
@login_required
def setting_youtube_revoke():
    """Revoke User's YouTube Crendential"""
    if not current_user.youtube_credentials:
        session["alert"] = "YouTube Credential isn't set"
        session["alert_type"] = "warning"
    else:
        response = current_user.youtube_revoke()
        if response is True:
            session["alert"] = "YouTube Access Revoke"
            session["alert_type"] = "success"
        else:
            session["alert"] = response
            session["alert_type"] = "danger"
    return redirect(url_for("user.setting"))

@user_blueprint.route("/setting/line-notify/authorize")
@login_required
def setting_line_notify_authorize():
    redirect_uri = url_for("user.setting_line_notify_oauth_callback", _external=True)
    return oauth.LineNotify.authorize_redirect(redirect_uri)

@user_blueprint.route("/setting/line-notify/oauth_callback")
@login_required
def setting_line_notify_oauth_callback():
    token = oauth.LineNotify.authorize_access_token()
    current_user.line_notify_init(token["access_token"])
    session["alert"] = "Line Notify Access Granted"
    session["alert_type"] = "success"
    return redirect(url_for("user.setting"))

@user_blueprint.route("/setting/line-notify/revoke")
@login_required
def setting_line_notify_revoke():
    """Revoke User's Line Notify Crendential"""
    if not current_user.line_notify_credentials:
        session["alert"] = "Line Notify Credential isn't set"
        session["alert_type"] = "warning"
    else:
        response = current_user.line_notify_revoke()
        if response is True:
            session["alert"] = "Line Notify Access Revoke"
            session["alert_type"] = "success"
        else:
            session["alert"] = response
            session["alert_type"] = "danger"
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
    credentials_dict = {
        "access_token": oauth_result.access_token,
        "account_id": oauth_result.account_id,
        "user_id": oauth_result.user_id,
        "url_state": oauth_result.url_state
    }
    current_user.dropbox_init(credentials_dict)
    session["alert"] = "Dropbx Access Granted"
    session["alert_type"] = "success"
    return redirect(url_for("user.setting"))

@user_blueprint.route("/setting/dropbox/revoke")
@login_required
def setting_dropbox_revoke():
    """Revoke User's Dropbx Crendential"""
    if not current_user.dropbox_credentials:
        session["alert"] = "Dropbx Credential isn't set"
        session["alert_type"] = "warning"
    else:
        response = current_user.dropbox_revoke()
        if response is True:
            session["alert"] = "Dropbx Access Revoke"
            session["alert_type"] = "success"
        else:
            session["alert"] = response
            session["alert_type"] = "danger"
    return redirect(url_for("user.setting"))
