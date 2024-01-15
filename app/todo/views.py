from flask import flash, render_template, redirect, url_for
from flask_login import login_required

from . import todo_blueprint
from .forms import CreateTodoForm
from .models import db, Todo

@todo_blueprint.route("/todo")
@login_required
def todo():
    form = CreateTodoForm()
    list = Todo.query.all()

    return render_template('todo.html', form=form, list=list)

@todo_blueprint.route("/create_todo", methods=['POST'])
def create_todo():
    form = CreateTodoForm()

    if form.validate_on_submit():
        task = form.task.data
        description = form.description.data
        todo = Todo(title=task, description=description, complete=False)
        db.session.add(todo)
        db.session.commit()
        flash("Створення виконано", category=("success"))
        return redirect(url_for("todo_bp.todo"))
    
    flash("Помилка при створенні", category=("danger"))
    return redirect(url_for("todo_bp.todo"))

@todo_blueprint.route("/read_todo/<int:todo_id>")
def read_todo(todo_id=None):
    todo = Todo.query.get_or_404(todo_id)
    return redirect(url_for("todo_bp.todo"))

@todo_blueprint.route("/update_todo/<int:todo_id>")
def update_todo(todo_id=None):
    todo = Todo.query.get_or_404(todo_id)

    todo.complete = not todo.complete
    db.session.commit()
    flash("Оновлення виконано", category=("success"))
    return redirect(url_for("todo_bp.todo"))

@todo_blueprint.route("/delete_todo/<int:todo_id>", methods=['POST'])
def delete_todo(todo_id=None):
    todo = Todo.query.get_or_404(todo_id)

    db.session.delete(todo)
    db.session.commit()
    flash("Видалення виконано", category=("success"))
    return redirect(url_for("todo_bp.todo"))