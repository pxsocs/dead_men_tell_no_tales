from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for, current_app)
from flask_login import (current_user, login_required, login_user, logout_user)
from werkzeug.security import generate_password_hash

from forms.user_forms import RegistrationForm, UpdateAccountForm
from models.user_models import User

user_routes = Blueprint('user_routes', __name__)


@user_routes.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hash = generate_password_hash(form.password.data)
            user = User.query.filter_by(username=current_user.username).first()
            user.password = hash
            current_app.db.session.commit()
            flash(f"Account password updated for user {current_user.username}",
                  "success")
            return redirect("/portfolio")

        flash("Password Change Failed. Something went wrong. Try Again.",
              "danger")

    return render_template("main/account.html",
                           title="Account",
                           form=form,
                           current_app=current_app)
