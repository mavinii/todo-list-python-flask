from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient

app = Flask(__name__)

# Instance of the MongoClient class from the PyMongo library
client = MongoClient('Your_mongodb_goes_here')

db = client.flask_db
todos = db.todos


# This code defines a Flask route handler for a todo list app, which inserts new items submitted via a form into a
# MongoDB database and renders the list of all todo items on the same page.
@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.insert_one({'content': content, 'degree': degree})
        return redirect(url_for('index'))

    all_todos = todos.find()
    return render_template('index.html', todos=all_todos)
