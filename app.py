from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt

app = Flask(__name__)  # It creates a new Flask application instance
bcrypt = Bcrypt(app)  # Bcrypt is a password hashing library

# MongoDB setup with secret key
client = MongoClient('mongodb+srv://user1:rjYKfcsRcgG6kMe1@cluster0.tbouul8.mongodb.net/?retryWrites=true&w=majority')
db = client.mydb
todos = db.todos
users = db.users

# Set the secret key to some unique value
app.secret_key = 'secret'


# It displays the home page with a login and register button
@app.route('/')
def home():
    return render_template('home.html')


# It displays the register page
@app.route('/register')
def register_form():
    return render_template('register.html')


# TODO: /register
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    user_registered = users.find_one({'username': username})

    # Create a new user if username is not registered
    if user_registered is None:
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        users.insert_one({'username': username, 'password': password_hash})
        return redirect(url_for('login'))
    return 'Username already registered!'.encode('utf-8')


# TODO: /login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.find_one({'username': username})

        # If user is not found, show an error message
        if user is None:
            return 'Invalid username or password'

        # Check if the password is correct using bcrypt
        # If so, redirect to the todo page
        if bcrypt.check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('todo'))
        return 'Invalid username or password'

    return render_template('login.html')


# TODO: /logout
@app.route('/logout')
def logout():
    # Remove the username from the session if it's there
    session.pop('user', None)
    return redirect(url_for('home'))


# Redirect the user to the login page if they're not logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for('login', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


# This code defines a Flask route handler for a to-do list app, which inserts new items submitted via a form into a
# MongoDB database and renders the list of all to-do items on the same page.
@app.route('/todo', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.insert_one({'content': content, 'degree': degree})

        # Redirect to the index page and shows the list updated
        return redirect(url_for('index'))

    # Find all todos in the database
    all_todos = todos.find()

    return render_template('index.html', todos=all_todos)


# Route for deleting the items of the list
@app.post('/<id>/delete/')
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))


# Debugging
if __name__ == '__main__':
    app.run(debug=True)
