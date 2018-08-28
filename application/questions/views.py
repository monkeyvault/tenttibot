from flask import redirect, render_template, request, url_for
from flask_login import current_user

from application import app, db, login_manager, login_required
from application.views import current_user_is_admin
from application.auth.models import User
from application.subjects.models import Subject
from application.questions.models import Question
from application.questions.forms import QuestionForm


@app.route("/<subject_id>", methods=["GET"])
def questions_index(subject_id):
    """Page for listing questions."""
    s = Subject.query.get(subject_id)
    q = Question.query.filter_by(subject_id=subject_id)
    a = User.find_author(subject_id)
    admin = current_user_is_admin()
    return render_template("questions/list.html", questions=q, subject_id=subject_id, subject_name=s.name, author=a.first(), admin=admin)


@app.route("/<subject_id>/new/", methods=["GET"])
@login_required()
def questions_form(subject_id):
    """Page for creating a new question"""
    s = Subject.query.get(subject_id)
    return render_template("questions/new.html", form=QuestionForm(), subject_id=subject_id, subject_name=s.name)


@app.route("/<subject_id>/<question_id>/", methods=["GET"])
@login_required()
def questions_question(subject_id, question_id):
    """Page for question editing"""
    form = QuestionForm(request.form)
    q = Question.query.get(question_id)
    s = Subject.query.get(subject_id)
    return render_template("questions/question.html", form=form, question=q, subject_name=s.name)


@app.route("/<subject_id>/<question_id>/edit/", methods=["POST"])
@login_required()
def questions_edit(subject_id, question_id):
    """Posting data to edit a question"""
    if not is_creator(subject_id) and not current_user_is_admin():
        return login_manager.unauthorized()

    form = QuestionForm(request.form)
    q = Question.query.get(question_id)
    s = Subject.query.get(subject_id)

    if not form.validate():
        return render_template("questions/question.html", form=form, question=q, subject_name=s.name)

    q.name = form.name.data
    q.answer = form.answer.data
    q.mastery = form.mastery.data

    db.session().commit()

    return redirect(url_for("questions_index", subject_id=subject_id))


@app.route("/<subject_id>/<question_id>/delete/", methods=["POST"])
@login_required()
def questions_delete(subject_id, question_id):
    """Deleting a question"""
    if not is_creator(subject_id) and not current_user_is_admin():
        return login_manager.unauthorized()

    q = Question.query.get(question_id)
    db.session().delete(q)
    db.session().commit()

    return redirect(url_for("questions_index", subject_id=subject_id))


@app.route("/<subject_id>/", methods=["POST"])
@login_required()
def questions_create(subject_id):
    """Post data to create a new question"""
    if not is_creator(subject_id):
        return login_manager.unauthorized()

    form = QuestionForm(request.form)

    if not form.validate():
        return render_template("questions/new.html", form=form, subject_id=subject_id)

    q = Question(form.name.data, form.answer.data, form.mastery.data)
    q.subject_id = subject_id

    db.session().add(q)
    db.session().commit()

    return redirect(url_for("questions_index", subject_id=subject_id))


def is_creator(subject_id):
    """Prevent users from adding to, editing or deleting material created by another user:"""
    s = Subject.query.get(subject_id)
    if s in current_user.subjects:
        return True
    return False
