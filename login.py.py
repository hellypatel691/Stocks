from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secret123'

DB_NAME = 'users.db'


# -------------------- DATABASE SETUP --------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            stock_symbol TEXT,
            quantity INTEGER
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS market (
            symbol TEXT PRIMARY KEY,
            company TEXT,
            price INTEGER,
            total_stocks INTEGER,
            sold_stocks INTEGER
)
''')
    
    c.execute("SELECT COUNT(*) FROM market")
    if c.fetchone()[0] == 0:
        market_data = [
        ('AAPL', 'Apple Inc.', 175, 10000, 2500),
        ('TSLA', 'Tesla Inc.', 1050, 8000, 3200),
        ('MSFT', 'Microsoft Corp.', 310, 12000, 4000)
    ]
        c.executemany(
            "INSERT INTO market VALUES (?, ?, ?, ?, ?)",
            market_data
        )

    conn.commit()
    conn.close()

init_db()

def init_portfolio():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            stock_symbol TEXT,
            quantity INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_portfolio()



@app.route('/portfolio')
def portfolio():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Get user's owned stocks
    c.execute("SELECT stock_symbol, quantity FROM portfolio WHERE username=?", (username,))
    owned_stocks = c.fetchall()

    # Get market stocks from DB
    c.execute("SELECT symbol, company, price, total_stocks, sold_stocks FROM market")
    market_stocks = c.fetchall()  # list of tuples

    conn.close()

    return render_template(
        'portfolio.html',
        market_stocks=market_stocks,  # now reading from DB
        owned_stocks=owned_stocks
    )

# -------------------- ROUTES --------------------

# Home / Login Page
@app.route('/')
def home():
    return render_template('login.html')

# Login Logic
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user is None:
        flash("Invalid username or password")
        return redirect(url_for('home'))

    session['username'] = username
    return redirect(url_for('dashboard'))

# Registration Page
@app.route('/register')
def register():
    return render_template('register.html')

# Registration Logic
@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        flash("Registration successful! Please login.")
        return redirect(url_for('home'))
    except sqlite3.IntegrityError:
        flash("Username already exists")
        return redirect(url_for('register'))
    finally:
        conn.close()

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html',username=session['username'])

# Buy / Sell Stocks
# Buy / Sell Stocks
@app.route('/trade', methods=['GET', 'POST'])
def trade():
    if 'username' not in session:
        return redirect(url_for('home'))

    username = session['username']
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Fetch user's current portfolio
    c.execute("SELECT stock_symbol, quantity FROM portfolio WHERE username=?", (username,))
    owned = {row[0]: row[1] for row in c.fetchall()}

    if request.method == 'POST':
        stock = request.form['stock_symbol']
        qty = int(request.form['quantity'])
        action = request.form['action']

        # Fetch market info for this stock
        c.execute("SELECT price, total_stocks, sold_stocks FROM market WHERE symbol=?", (stock,))
        price, total_stocks, sold_stocks = c.fetchone()

        available = total_stocks - sold_stocks
        owned_qty = owned.get(stock, 0)

        # ---------------- BUY ----------------
        if action == 'buy':
            if qty > available:
                flash("Not enough stocks available")
                return redirect(url_for('trade'))

            # Update user portfolio
            if owned_qty == 0:
                c.execute(
                    "INSERT INTO portfolio (username, stock_symbol, quantity) VALUES (?, ?, ?)",
                    (username, stock, qty)
                )
            else:
                c.execute(
                    "UPDATE portfolio SET quantity=? WHERE username=? AND stock_symbol=?",
                    (owned_qty + qty, username, stock)
                )

            # Update market sold stocks
            c.execute(
                "UPDATE market SET sold_stocks = sold_stocks + ? WHERE symbol=?",
                (qty, stock)
            )

            flash(f"Bought {qty} shares of {stock}")

        # ---------------- SELL ----------------
        elif action == 'sell':
            if qty > owned_qty:
                flash("Not enough stock to sell")
                return redirect(url_for('trade'))

            new_qty = owned_qty - qty
            if new_qty == 0:
                c.execute(
                    "DELETE FROM portfolio WHERE username=? AND stock_symbol=?",
                    (username, stock)
                )
            else:
                c.execute(
                    "UPDATE portfolio SET quantity=? WHERE username=? AND stock_symbol=?",
                    (new_qty, username, stock)
                )

            # Update market sold stocks
            c.execute(
                "UPDATE market SET sold_stocks = sold_stocks - ? WHERE symbol=?",
                (qty, stock)
            )

            flash(f"Sold {qty} shares of {stock}")

        conn.commit()
        conn.close()
        return redirect(url_for('trade'))

    # For GET request: show market and portfolio
    c.execute("SELECT symbol, company, price, total_stocks, sold_stocks FROM market")
    market = c.fetchall()  # list of tuples
    conn.close()
    return render_template('buy_sell.html', market=market, owned=owned)

@app.route('/stocks')
def available_stocks():
    if 'username' not in session:
        return redirect(url_for('home'))

    # Example list of available stocks (symbol, company, price)
    stocks = [
        {'symbol': 'AAPL', 'company': 'Apple Inc.', 'price': 175.50},
        {'symbol': 'GOOGL', 'company': 'Alphabet Inc.', 'price': 2850.30},
        {'symbol': 'AMZN', 'company': 'Amazon.com, Inc.', 'price': 3450.00},
        {'symbol': 'TSLA', 'company': 'Tesla, Inc.', 'price': 1050.75},
        {'symbol': 'MSFT', 'company': 'Microsoft Corp.', 'price': 310.20}
    ]

    return render_template('stocks.html', stocks=stocks)
    

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)