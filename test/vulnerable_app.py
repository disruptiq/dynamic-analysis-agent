#!/usr/bin/env python3
"""
Vulnerable Flask Application for Testing Dynamic Analysis Agent

This application contains several known vulnerabilities:
1. SQL Injection in login form
2. XSS in search functionality
3. Command Injection in system info endpoint
4. Directory Traversal in file viewer
5. Authentication bypass
6. Information disclosure
"""

from flask import Flask, request, render_template_string, send_file, jsonify
import sqlite3
import os
import subprocess
import json

app = Flask(__name__)

# Create a simple database with vulnerable data
def init_db():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)''')

    # Insert test data
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'password123', 'admin@test.com')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'user', 'user123', 'user@test.com')")
    c.execute("INSERT OR IGNORE INTO users VALUES (3, 'test', 'test123', 'test@test.com')")

    conn.commit()
    conn.close()

init_db()

# Templates
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h1>Login</h1>
    <form method="POST" action="/login">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    <div>{{ message }}</div>
</body>
</html>
"""

SEARCH_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Search</title></head>
<body>
    <h1>Search Users</h1>
    <form method="GET" action="/search">
        Query: <input type="text" name="q" value="{{ query }}">
        <input type="submit" value="Search">
    </form>
    <div>{{ results|safe }}</div>
</body>
</html>
"""

ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Admin Panel</title></head>
<body>
    <h1>Admin Panel</h1>
    <h2>System Information</h2>
    <form method="GET" action="/system">
        Command: <input type="text" name="cmd" value="whoami">
        <input type="submit" value="Execute">
    </form>
    <div>{{ output|safe }}</div>

    <h2>File Viewer</h2>
    <form method="GET" action="/file">
        File: <input type="text" name="file" value="test.txt">
        <input type="submit" value="View">
    </form>
    <div>{{ content|safe }}</div>
</body>
</html>
"""

@app.route('/')
def index():
    return '''
    <h1>Vulnerable Test Application</h1>
    <p>This application contains several vulnerabilities for testing purposes.</p>
    <ul>
        <li><a href="/login">Login (SQL Injection)</a></li>
        <li><a href="/search">Search (XSS)</a></li>
        <li><a href="/admin">Admin Panel (Command Injection & Directory Traversal)</a></li>
        <li><a href="/api/users">API (Information Disclosure)</a></li>
    </ul>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # VULNERABILITY: SQL Injection
        conn = sqlite3.connect('test.db')
        c = conn.cursor()

        # Dangerous: direct string formatting in SQL query
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"DEBUG: Executing query: {query}")  # Information disclosure

        try:
            c.execute(query)
            user = c.fetchone()
            if user:
                message = f"Welcome, {user[1]}!"
            else:
                message = "Invalid credentials"
        except Exception as e:
            message = f"Database error: {str(e)}"  # Error disclosure

        conn.close()

    return render_template_string(LOGIN_TEMPLATE, message=message)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = ""

    if query:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()

        # VULNERABILITY: SQL Injection in search
        search_query = f"SELECT username, email FROM users WHERE username LIKE '%{query}%' OR email LIKE '%{query}%'"
        print(f"DEBUG: Search query: {search_query}")  # Information disclosure

        try:
            c.execute(search_query)
            users = c.fetchall()
            if users:
                results = "<h2>Results:</h2><ul>"
                for user in users:
                    # VULNERABILITY: XSS - direct output without sanitization
                    results += f"<li>{user[0]} - {user[1]}</li>"
                results += "</ul>"
            else:
                results = "No results found"
        except Exception as e:
            results = f"Search error: {str(e)}"

        conn.close()

        # VULNERABILITY: XSS in query reflection
        results += f"<p>You searched for: {query}</p>"

    return render_template_string(SEARCH_TEMPLATE, query=query, results=results)

@app.route('/admin')
def admin():
    return render_template_string(ADMIN_TEMPLATE, output="", content="")

@app.route('/system')
def system():
    cmd = request.args.get('cmd', 'whoami')
    output = ""

    # VULNERABILITY: Command Injection
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = f"<pre>Command: {cmd}\nOutput:\n{result.stdout}\nErrors:\n{result.stderr}</pre>"
    except Exception as e:
        output = f"<pre>Error executing command: {str(e)}</pre>"

    return render_template_string(ADMIN_TEMPLATE, output=output, content="")

@app.route('/file')
def file_viewer():
    filename = request.args.get('file', 'test.txt')
    content = ""

    # VULNERABILITY: Directory Traversal
    try:
        # No path sanitization
        with open(filename, 'r') as f:
            content = f"<pre>{f.read()}</pre>"
    except Exception as e:
        content = f"<pre>Error reading file: {str(e)}</pre>"

    return render_template_string(ADMIN_TEMPLATE, output="", content=content)

@app.route('/api/users')
def api_users():
    # VULNERABILITY: Information Disclosure - exposes all user data
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    # Return sensitive data as JSON
    return jsonify([{
        'id': user[0],
        'username': user[1],
        'password': user[2],  # Password exposure!
        'email': user[3]
    } for user in users])

@app.route('/debug')
def debug():
    # VULNERABILITY: Information Disclosure
    info = {
        'environment': dict(os.environ),
        'current_dir': os.getcwd(),
        'files': os.listdir('.'),
        'python_version': os.sys.version,
        'database_exists': os.path.exists('test.db')
    }
    return jsonify(info)

if __name__ == '__main__':
    print("Starting vulnerable test application...")
    print("Available endpoints:")
    print("  / - Home page")
    print("  /login - SQL Injection vulnerability")
    print("  /search - XSS vulnerability")
    print("  /admin - Admin panel")
    print("  /system - Command injection")
    print("  /file - Directory traversal")
    print("  /api/users - Information disclosure")
    print("  /debug - Debug information disclosure")
    app.run(host='0.0.0.0', port=5000, debug=True)
