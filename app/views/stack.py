# flake8: noqa E712
from flask import Blueprint, request, flash, jsonify
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


@bp.route("/delete", methods=["DELETE"])
@login_required
def delete():
    form = f.NewStackForm(request.form)
    stack: str = form.stacks.data  # -check-untyped-defs

    if stack:
        try:
            stack_object = db.session.query(m.Stack).filter_by(name=stack)
            stack_object.delete()
            db.session.commit()

        except Exception as e:
            db.session.rollback()

            cases_with_stack = (
                db.session.query(m.Case)
                .filter(m.Case._stacks.any(m.Stack.name == stack))
                .all()
            )

            title_list: list[str] = []

            for case in cases_with_stack:
                title_list.append(case.title)

            return jsonify(title_list), 422

    else:
        log(log.INFO, "Deletion failed. Stack: [%s]", stack)
        flash("Deletion failed", "danger")
        return "ok", 422

    log(log.INFO, "Stack deleted!. Stack: [%s]", stack)
    flash("Successfully deleted!", "success")
    return "ok", 200
