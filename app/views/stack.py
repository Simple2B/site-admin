# flake8: noqa E712
from flask import (
    Blueprint,
    request,
    flash,
)
from flask_login import login_required

from app.common import models as m
from app import forms as f
from app.logger import log
from app.database import db



bp = Blueprint("stack", __name__, url_prefix="/stack")

@bp.route("/create", methods=["POST"])
@login_required
def create():
    form = f.NewStackForm(request.form)

    if form.validate_on_submit():
        stacks = form.stacks.data.split(",")
        for stack in stacks:
            new_stack = m.Stack(name=stack)
            db.session.add(new_stack)
            db.session.commit()
    else:
        flash("Invalid form data or stack exist", "danger")
        return "ok", 422

    log(log.INFO, "Stack created!. Stack: [%s]", new_stack.name)
    flash("Stack created!", "success")
    return "ok", 200