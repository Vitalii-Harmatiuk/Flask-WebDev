from flask import Flask, flash, render_template, request, redirect, url_for, json, make_response, session
import os
from datetime import datetime
from app import app
from .forms import LoginForm, ChangePasswordForm, CreateTodoForm, CreateFeedbackForm
from .models import db, Todo, Feedback
import random

my_skills = ("C++", "HTML & CSS", "PostgresSQL", "Photopea", "Java", "Python")

def get_user_info():
    user_os = os.name
    user_agent = request.headers.get('User-Agent')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return user_os, user_agent, current_time

@app.route('/base')
def index():
    user_os, user_agent, current_time = get_user_info()
    return render_template('base.html', user_os=user_os, user_agent=user_agent, current_time=current_time)

@app.route('/home')
@app.route('/')
def home():
    user_os, user_agent, current_time = get_user_info()
    return render_template('home.html', user_os=user_os, user_agent=user_agent, current_time=current_time)

@app.route('/cv')
def cv():
    return render_template('cv.html')

@app.route('/edu')
def edu():
    return render_template('edu.html')

@app.route('/hobbies')
def hobbies():
    return render_template('hobbies.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    filename = os.path.join(app.static_folder, 'data', 'auth.json')
    with open(filename) as auth_file:
        data = json.load(auth_file)

    json_name = data['name']
    json_password = data['password']

    if form.validate_on_submit():
        form_name = form.username.data
        form_password = form.password.data
        form_remember = form.remember.data

        if json_name == form_name and json_password == form_password:
            if form_remember:
                user_id = random.randint(1, 10000)
                session['userId'] = user_id
                session['name'] = form_name
                session['password'] = form_password
                flash("Вхід виконано", category=("success"))
                return redirect(url_for('info', user=session['name']))
            else:
                flash("Ви не запамʼятали себе, введіть дані ще раз", category=("warning"))
                return redirect(url_for('home'))
        else:
            flash("Вхід не виконано", category=("warning"))
            return redirect(url_for('login'))
    
    return render_template('login.html', form=form)

@app.route('/info', methods=['GET'])
def info():
    cookies = request.cookies
    form = ChangePasswordForm()

    return render_template('info.html', cookies=cookies, form=form)

@app.route('/logout')
def logout():
    session.pop('userId')
    session.pop('name')
    session.pop('password')    
    return redirect(url_for("login"))

@app.route('/skills/')
@app.route('/skills/<int:id>')
def skills(id=None):
    if id is not None:
        if 0 <= id < len(my_skills):
            skill = my_skills[id]
            return render_template('skills.html', skill=skill)
        else:
            return render_template('skills.html')
    else:
        return render_template('skills.html', skills=my_skills, total_skills=len(my_skills))

def set_cookie(key, value, max_age):
    response = make_response(redirect('info'))
    response.set_cookie(key, value, max_age=max_age)
    return response

def delete_cookie(key):
    response = make_response(redirect('info'))
    response.delete_cookie(key)
    return response

@app.route('/add_cookie', methods=['POST'])
def add_cookie():
    key = request.form.get('key')
    value = request.form.get('value')
    max_age = int(request.form.get('max_age'))

    flash("Кукі додано", category=("success"))
    return set_cookie(key, value, max_age)

@app.route('/remove_cookie/', methods=['GET'])
@app.route('/remove_cookie/<key>', methods=['GET'])
def remove_cookie():

    key = request.args.get('key')

    if key:
        flash("Кукі видалено", category=("dark"))
        response = make_response(redirect(url_for('info')))
        response.delete_cookie(key)
        return response
    else:
        flash("Виникла помилка. Повідомте про ключ нам", category=("info"))
        response = make_response(redirect(url_for('info')))
        return response

@app.route('/remove_all_cookies', methods=['GET'])
def remove_all_cookies():
    flash("Усі кукі видалено", category=("danger"))
    response = make_response(redirect(url_for('info')))
    cookies = request.cookies

    for key in cookies.keys():
        if key != 'session':
            response.delete_cookie(key)

    return response

@app.route('/change_password', methods=['POST'])
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        new_password = form.password.data
        confirm_new_password = form.confirm_password.data
        if new_password != '':
            if new_password == confirm_new_password:
                session['password'] = new_password

                filename = os.path.join(app.static_folder, 'data', 'auth.json')
                with open(filename) as auth_file:
                    data = json.load(auth_file)

                new_admin_data = {
                    'name': data['name'],
                    'password': new_password
                }

                new_passwd_json = json.dumps(new_admin_data, indent=2)

                with open(filename, "w") as outfile:
                    outfile.write(new_passwd_json)

                flash("Пароль успішно змінено", category=("success"))
                return redirect(url_for('info'))

            flash("Ви не змінили пароль", category=("danger"))
            return redirect(url_for('info'))

    flash("Ви неправильно набрали пароль. Спробуйте ще раз", category=("danger"))
    return redirect(url_for('info'))

@app.route("/todo")
def todo():
    form = CreateTodoForm()
    list = db.session.query(Todo).all()

    return render_template('todo.html', form=form, list=list)

@app.route("/create_todo", methods=['POST'])
def create_todo():
    form = CreateTodoForm()

    if form.validate_on_submit():
        task = form.task.data
        description = form.description.data
        todo = Todo(title=task, description=description, complete=False)
        db.session.add(todo)
        db.session.commit()
        flash("Створення виконано", category=("success"))
        return redirect(url_for("todo"))
    
    flash("Помилка при створенні", category=("danger"))
    return redirect(url_for("todo"))

@app.route("/read_todo/<int:todo_id>")
def read_todo(todo_id=None):
    todo = Todo.query.get_or_404(todo_id)
    return redirect(url_for("todo"))

@app.route("/update_todo/<int:todo_id>")
def update_todo(todo_id=None):
    todo = Todo.query.get_or_404(todo_id)

    todo.complete = not todo.complete
    db.session.commit()
    flash("Оновлення виконано", category=("success"))
    return redirect(url_for("todo"))

@app.route("/delete_todo/<int:todo_id>")
def delete_todo(todo_id=None):
    todo = Todo.query.get_or_404(todo_id)

    db.session.delete(todo)
    db.session.commit()
    flash("Видалення виконано", category=("success"))
    return redirect(url_for("todo"))

@app.route("/feedback")
def feedback():
    feedback_form = CreateFeedbackForm()
    feedback_list = db.session.query(Feedback).all()

    return render_template('feedback.html', feedback_form=feedback_form, feedback_list=feedback_list)

@app.route("/create_feedback", methods=['POST'])
def create_feedback():
    feedback_form = CreateFeedbackForm()

    if feedback_form.validate_on_submit():
        name = feedback_form.name.data
        email = feedback_form.email.data
        description = feedback_form.description.data
        rate = feedback_form.rate.data

        new_feedback = Feedback(name=name, email=email, description=description, rate=rate, ukr_user=False)

        db.session.add(new_feedback)
        db.session.commit()
        flash("Створення виконано", category=("success"))
        return redirect(url_for("feedback"))

    flash("Помилка при створенні", category=("danger"))
    return redirect(url_for("feedback"))

@app.route("/read_feedback/<int:feedback_id>")
def read_feedback(feedback_id=None):
    feedback = Feedback.query.get_or_404(feedback_id)
    return redirect(url_for("feedback"))

@app.route("/delete_feedback/<int:feedback_id>")
def delete_feedback(feedback_id=None):
    feedback = Feedback.query.get_or_404(feedback_id)

    db.session.delete(feedback)
    db.session.commit()
    flash("Видалення виконано", category=("success"))
    return redirect(url_for("feedback"))

@app.route("/update_feedback/<int:feedback_id>")
def update_feedback(feedback_id=None):
    feedback = Feedback.query.get_or_404(feedback_id)

    feedback.ukr_user = not feedback.ukr_user
    db.session.commit()
    flash("Оновлення виконано", category=("success"))
    return redirect(url_for("feedback"))

@app.route("/main")
def main():
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)