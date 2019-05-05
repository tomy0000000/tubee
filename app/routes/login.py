"""Routes involves user credentials"""
from flask import Blueprint, g, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user, login_required
from ..forms import LoginForm
from ..models import User
login = Blueprint("login", __name__)

@login.route("/", methods=["GET", "POST"])
def root_login():
    """Root Page for User Login"""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            login_user(user)
            return redirect(url_for("main.dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", form=form, error=error)

@login.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout from the System"""
    logout_user()
    return redirect(url_for("login.root_login"))

@login.route("/login/setting", methods=["GET", "POST"])
@login_required
def login_setting():
    """"""
    notes = ""
    return render_template("setting.html", user=current_user, notes=notes)
