# // simple flask app
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
app = Flask(__name__)
app.secret_key = 'hello'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=1)
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


#create database if it is not present

if not os.path.exists('instance/todo.sqlite3'):
    with app.app_context():
        db.create_all()




@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        if request.method == 'POST':
            for task in tasks:
                task.completed = 'completed' + str(task.id) in request.form
            db.session.commit()
        return render_template('index.html', tasks=tasks)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
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
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'



if __name__ == "__main__":
    app.run(debug=True)