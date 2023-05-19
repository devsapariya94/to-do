    # // simple flask app
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import json
import hashlib

app = Flask(__name__)
app.secret_key = 'hello'
login_manager = LoginManager(app)
app.permanent_session_lifetime = timedelta(days=1)



with open('config.json', 'r') as c:
    params = json.load(c)["params"]


DB_NAME = "database.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(DB_NAME)

app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql://{params["db_username"]}:{params["db_passw"]}@{params["db_host"]}/{params["db_name"]}'

db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


#create database if it is not present
# print(os.path.exists(DB_NAME))
# if not os.path.exists(DB_NAME):
#     with app.app_context():
#         db.create_all()
#     print('Created Database!')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/', methods=['POST', 'GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == 'POST':
        print(11111111111111)
        task_content = request.form['content']
        userid = current_user.id
        new_task = Todo(content=task_content, user=userid)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks= Todo.query.filter_by(user=current_user.id).order_by(Todo.date_created).all()
        if request.method == 'POST':
            for task in tasks:
                task.completed = 'completed' + str(task.id) in request.form
            db.session.commit()
        return render_template('index.html', tasks=tasks)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.completed = 'completed' in request.form  # update completion status

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)

@app.route('/complete/<int:id>', methods=['GET', 'POST'])
def complete(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.completed = not task.completed

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating the task status'
    

    
@app.route('/delete/<int:id>', methods=['GET', 'DELETE'])
def delete(id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(email=email).first()
        if user:
            if password == user.password:
                login_user(user, remember=True)
                return redirect(url_for('index'))
        flash(message='Invalid credentials or user is not exist', category='error')
        return redirect(location=url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(email=email).first()
        if user:
            flash(message='Email already exists', category='error')
            return redirect(url_for('signup'))
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully, please login')
        return redirect(url_for('login'))
    return render_template('signup.html')




if __name__ == "__main__":
    app.run(debug=True)