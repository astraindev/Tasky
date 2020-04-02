from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from server import app, db
from server.forms.add_task import AddTaskForm
from server.forms.complete_task import CompleteTaskForm
from server.forms.login import LoginForm
from server.forms.remove_task import RemoveTaskForm
from server.forms.signup import SignupForm
from server.models.taskyuser import TaskyUser
from server.models.taskytask import TaskyTask


@app.route('/')
def index():
    return redirect(url_for('main_menu'))


@app.route('/main_menu')
@login_required
def main_menu():
    return render_template('main_menu.html.j2')


@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = AddTaskForm()
    if form.validate_on_submit():
        if len(form.task_text.data) > 140:
            flash('Task is too verbose. Needs to be 140 characters or less.')
            return redirect(url_for('add_task'))
        task = TaskyTask()
        task.task = form.task_text.data
        task.complete = False
        task.user_id = current_user.id
        db.session.add(task)
        db.session.commit()
        flash('Task added')
        return redirect(url_for('main_menu'))
    return render_template('add_task.html.j2', title='Add Task', form=form)


@app.route('/remove_task', methods=['GET', 'POST'])
@login_required
def remove_task():
    form = RemoveTaskForm()
    form.task_id.choices = [(t.id, t.task) for t in TaskyTask.query.filter_by(user_id=current_user.id)]

    if form.validate_on_submit():
        task = TaskyTask.query.filter_by(id=form.task_id.data).first()
        db.session.delete(task)
        db.session.commit()
        flash('Task removed')
        return redirect(url_for('main_menu'))

    return render_template('remove_task.html.j2', title='Remove Task', form=form)


@app.route('/complete_task', methods=['GET', 'POST'])
@login_required
def complete_task():
    form = CompleteTaskForm()
    form.task_id.choices = [(t.id, t.task) for t in TaskyTask.query.filter_by(user_id=current_user.id).filter_by(complete=False)]

    if form.validate_on_submit():
        task = TaskyTask.query.filter_by(id=form.task_id.data).first()
        task.complete = True
        db.session.add(task)
        db.session.commit()
        flash('Task completed')
        return redirect(url_for('main_menu'))

    return render_template('remove_task.html.j2', title='Remove Task', form=form)


@app.route('/list_tasks')
@login_required
def list_tasks():
    return render_template('list_tasks.html.j2', title='List Tasks', tasks=current_user.tasks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_menu'))
    form = LoginForm()
    if form.validate_on_submit():
        user = TaskyUser.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main_menu')
        return redirect(next_page)
    return render_template('login.html.j2', title='Log In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_menu'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main_menu'))
    form = SignupForm()
    if form.validate_on_submit():
        user = TaskyUser()
        user.username = form.username.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a new user!')
        return redirect(url_for('login'))
    return render_template('signup.html.j2', title='Signup', form=form)


@app.errorhandler(404)
@app.route("/error404")
def page_not_found(error):
    return app.send_static_file('404.html')


@app.errorhandler(500)
@app.route("/error500")
def requests_error(error):
    return app.send_static_file('500.html')
