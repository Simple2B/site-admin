# flake8: noqa E712
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from flask_login import login_required
import sqlalchemy as sa
from app.controllers import create_pagination

from app.common import models as m
from app import forms as f
from app.logger import log
from app.database import db


bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    q = request.args.get("q", type=str, default=None)
    query = (
        m.Question.select()
        .where(m.Question.is_deleted == False)
        .order_by(m.Question.id)
    )
    count_query = sa.select(sa.func.count()).select_from(m.Question)
    form = f.NewQuestionForm()
    if q:
        query = (
            m.Question.select()
            .where(
                sa.and_(m.Question.text.like(f"{q}%"), m.Question.is_deleted == False)
            )
            .order_by(m.Question.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(
                sa.and_(m.Question.text.like(f"{q}%"), m.Question.is_deleted == False)
            )
            .select_from(m.Question)
        )

    pagination = create_pagination(total=db.session.scalar(count_query))

    return render_template(
        "quiz/quizes.html",
        questions=db.session.execute(
            query.offset((pagination.page - 1) * pagination.per_page).limit(
                pagination.per_page
            )
        ).scalars(),
        page=pagination,
        search_query=q,
        form=form,
    )


@bp.route("/get/<int:id>", methods=["GET"])
@login_required
def get(id: int):
    question: m.Question = db.session.scalar(
        m.Question.select().where(m.Question.id == id)
    )
    if not question:
        log(log.INFO, "There is no question with id: [%s]", id)
        flash("There is no such question", "danger")
        return "no question", 404

    return question.s_dict()


@bp.route("/save", methods=["POST"])
@login_required
def save():
    form = f.EditQuestionForm()
    if form.validate_on_submit():
        query = m.Question.select().where(m.Question.id == int(form.id.data))
        question: m.Question | None = db.session.scalar(query)
        if not question:
            log(log.ERROR, "Not found question by id : [%s]", form.id.data)
            flash("Cannot save question data", "danger")
        question.text = form.text.data
        question.correct_answer_mark = form.correct_answer_mark.data
        question.save()
        for i in range(1, 5):
            query = m.VariantAnswer.select().where(
                m.VariantAnswer.question_id == question.id,
                m.VariantAnswer.answer_mark == i,
            )
            variant: m.VariantAnswer | None = db.session.scalar(query)
            if not variant:
                log(log.ERROR, "Not found variant by id : [%s]", question.id)
                flash("Cannot save user data", "danger")
            else:
                variant.text = form[f"variant_{i}"].data
                db.session.add(variant)
                db.session.commit()
        return redirect(url_for("quiz.get_all"))
    else:
        log(log.ERROR, "Question save errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
        return redirect(url_for("quiz.get_all"))


@bp.route("/create", methods=["POST"])
@login_required
def create():
    form = f.NewQuestionForm()
    if form.validate_on_submit():
        question = m.Question(
            text=form.text.data,
            correct_answer_mark=form.correct_answer_mark.data,
        )
        question.save()
        for i in range(1, 5):
            variant = m.VariantAnswer(
                question_id=question.id,
                text=form[f"variant_{i}"].data,
                answer_mark=i,
            )
            db.session.add(variant)
        db.session.commit()

        log(log.INFO, "Form submitted. Question: [%s]", question)
        flash("Question added!", "success")
        question.save()
        return redirect(url_for("quiz.get_all"))
    else:
        log(log.ERROR, "Question save errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
        return redirect(url_for("quiz.get_all"))


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id: int):
    question = db.session.scalar(m.Question.select().where(m.Question.id == id))
    if not question:
        log(log.INFO, "There is no question with id: [%s]", id)
        flash("There is no such question", "danger")
        return "no question", 404
    question.is_deleted = True
    db.session.commit()
    log(log.INFO, "question deleted. question: [%s]", question)
    flash("question deleted!", "success")
    return "ok", 200
