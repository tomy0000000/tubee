"""Routes involves user credentials"""
from flask import Blueprint, current_app, redirect, request, render_template, session, url_for
from flask_login import current_user, login_user, logout_user, login_required
from ..forms import LoginForm, RegisterForm
from ..helper import build_youtube_flow
from ..models import User
user = Blueprint("user", __name__)

@user.route("/register", methods=["GET", "POST"])
def register():
    """User Register"""
    if current_user.is_authenticated:
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

@user.route("/login", methods=["GET", "POST"])
def login():
    """User Login"""
    if current_user.is_authenticated:
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

@user.route("/logout", methods=["GET"])
@login_required
def logout():
    """User Logout"""
    logout_user()
    session["login_message_body"] = "You've Logged Out"
    session["login_message_type"] = "success"
    return redirect(url_for("user.login"))

@user.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    """User Setting Page"""
    alert = session.pop("action_response_message", None)
    alert_type = session.pop("action_response_status", None)
    return render_template("setting.html",
                           alert=alert,
                           alert_type=alert_type)

@user.route('/setting/youtube/authorize')
@login_required
def setting_youtube_authorize():
    flow = build_youtube_flow()
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true")
    session["state"] = state
    return redirect(authorization_url)

@user.route("/setting/youtube/oauth_callback")
@login_required
def setting_youtube_oauth_callback():
    flow = build_youtube_flow(state=session["state"])
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
        session["action_response_message"] = "YouTube Access Granted"
        session["action_response_status"] = "success"
    else:
        session["action_response_message"] = "YouTube Access Failed"
        session["action_response_status"] = "danger"
    return redirect(url_for("user.setting"))

@user.route("/setting/youtube/revoke")
@login_required
def setting_youtube_revoke():
    """Revoke User's YouTube Crendential"""
    if not current_user.youtube_credentials:
        session["action_response_message"] = "YouTube Credential isn't set"
        session["action_response_status"] = "warning"
    else:
        response = current_user.youtube_revoke()
        if response is True:
            session["action_response_message"] = "YouTube Access Revoke"
            session["action_response_status"] = "success"
        else:
            session["action_response_message"] = response
            session["action_response_status"] = "danger"
    return redirect(url_for("user.setting"))
