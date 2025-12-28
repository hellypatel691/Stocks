from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create database if it doesn't exist
db_path = 'users.db'
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

# Home / Login page
@app.route('/')
def home():
    return render_template('login.html')

# Login logic
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('home'))

# Registration page
@app.route('/register')
def register():
    return render_template('register.html')

# Registration logic
@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('home'))
    except sqlite3.IntegrityError:
        flash('Username already exists')
        return redirect(url_for('register'))
    finally:
        conn.close()

# Dashboard page
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Hello, {session['username']}! Welcome to your dashboard."
    else:
        return redirect(url_for('home'))

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)



    # Show registration form
@app.route('/register')
def show_register():
    return render_template('register.html')

# Handle registration form submission
@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('home'))
    except sqlite3.IntegrityError:
        flash('Username already exists')
        return redirect(url_for('show_register'))
    finally:
        conn.close()