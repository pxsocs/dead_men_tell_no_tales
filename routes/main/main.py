import ast
from email.policy import default
import json
import dateutil.parser as parser
from datetime import datetime
from flask import (Blueprint, render_template, current_app, redirect, flash,
                   url_for, request)
from flask_login import (login_required, login_user, current_user, logout_user)
from forms.user_forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_models import User
from sqlalchemy import desc

main = Blueprint('main', __name__)

# Minimum TemplateData used for render_template in all routes
templateData = {
    "title": "Project Salazar",
}


# Landing Page
@main.route("/login", methods=['GET', 'POST'])
def login():

    # Check if logged in - if so, redirect to main page
    if current_user.is_authenticated:
        flash(f"Logged in as {current_user.username}.", "success")
        return redirect("/portfolio")

    # Process the validate on submit methods

    # LOGIN USER
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash(f"Login Successful. Welcome {user}.", "success")
            next_page = request.args.get("next")  # get the original page
            if next_page:
                return redirect(next_page)
            else:
                return redirect("/main")
        else:
            flash("Login failed. Please check Username and Password", "danger")

    # CREATE NEW ACCOUNT
    signup_form = RegistrationForm()
    if signup_form.validate_on_submit():
        hash = generate_password_hash(signup_form.password.data)
        user = User(username=signup_form.username.data, password=hash)
        current_app.db.session.add(user)
        current_app.db.session.commit()
        login_user(user, remember=True)
        flash(
            f"Account created for {signup_form.username.data}. User Logged in.",
            "success")
        return redirect("/main")

    # Include data to be passed into html
    templateData['title'] = "Welcome"
    templateData['form'] = form
    templateData['signup_form'] = signup_form
    return (render_template('main/index.html', **templateData))


@main.route("/logout")
def logout():
    logout_user()
    return redirect("/")


# Portfolio editing and including
@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
@main.route("/main", methods=['GET', 'POST'])
def portfolio():
    templateData['title'] = "Home"
    return (render_template('main/index.html', **templateData))
