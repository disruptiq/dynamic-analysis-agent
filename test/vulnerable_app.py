#!/usr/bin/env python3
"""
Multi-Service Vulnerable Application for Testing Dynamic Analysis Agent

This application runs multiple services on different ports with various vulnerabilities:
1. HTTP Flask App (port 8080) - Web vulnerabilities
2. HTTPS Flask App (port 8443) - SSL-enabled web vulnerabilities
3. Simple TCP Service (port 9000) - Basic TCP server with vulnerabilities
4. Alternative HTTP Service (port 3000) - Different web framework simulation

Vulnerabilities included:
- SQL Injection in login forms
- XSS in search functionality
- Command Injection in system endpoints
- Directory Traversal in file viewers
- Authentication bypass
- Information disclosure
- SSL/TLS misconfigurations
- TCP service vulnerabilities
"""

from flask import Flask, request, render_template_string, send_file, jsonify
import sqlite3
import os
import subprocess
import json
import threading
import socket
import ssl
import time
import ipaddress
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

# Create multiple Flask applications for different ports
app_http = Flask(__name__)  # HTTP on port 8080
app_https = Flask(__name__)  # HTTPS on port 8443
app_alt = Flask(__name__)   # Alternative HTTP on port 3000

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

# Simple TCP Server with vulnerabilities
class VulnerableTCPServer:
    def __init__(self, host='0.0.0.0', port=9000):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        """Start the TCP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"TCP Server started on {self.host}:{self.port}")

            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"TCP Connection from {client_address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
        except Exception as e:
            print(f"TCP Server error: {e}")

    def handle_client(self, client_socket, client_address):
        """Handle individual client connections with vulnerabilities"""
        try:
            # VULNERABILITY: Buffer overflow potential
            data = client_socket.recv(1024).decode('utf-8').strip()
            print(f"Received from {client_address}: {data}")

            if not data:
                client_socket.close()
                return

            # VULNERABILITY: Command injection via eval
            if data.startswith("EVAL "):
                try:
                    result = str(eval(data[5:]))  # Dangerous eval!
                    response = f"Result: {result}\n"
                except Exception as e:
                    response = f"Error: {str(e)}\n"
            elif data.startswith("EXEC "):
                try:
                    # VULNERABILITY: Command execution
                    result = subprocess.run(data[5:], shell=True, capture_output=True, text=True)
                    response = f"Output: {result.stdout}\nErrors: {result.stderr}\n"
                except Exception as e:
                    response = f"Execution error: {str(e)}\n"
            elif data.startswith("READ "):
                try:
                    # VULNERABILITY: Path traversal
                    filename = data[5:]
                    with open(filename, 'r') as f:
                        content = f.read()
                    response = f"File content:\n{content}\n"
                except Exception as e:
                    response = f"File read error: {str(e)}\n"
            else:
                response = f"Echo: {data}\nAvailable commands: EVAL <code>, EXEC <command>, READ <file>\n"

            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()

# Alternative HTTP Server (simple Python HTTP server)
class VulnerableHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests with vulnerabilities"""
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = """
            <html>
            <head><title>Alternative Vulnerable Service</title></head>
            <body>
                <h1>Alternative Vulnerable HTTP Service</h1>
                <p>This is a simple HTTP server with vulnerabilities.</p>
                <ul>
                    <li><a href="/info">System Info</a></li>
                    <li><a href="/files">File Listing</a></li>
                    <li><a href="/env">Environment Variables</a></li>
                </ul>
            </body>
            </html>
            """
            self.wfile.write(response.encode())

        elif self.path.startswith("/info"):
            # VULNERABILITY: Command injection
            cmd = self.path.split("?", 1)[1] if "?" in self.path else "whoami"
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                output = f"Command: {cmd}<br>Output: {result.stdout}<br>Errors: {result.stderr}"
            except Exception as e:
                output = f"Error: {str(e)}"

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>System Info</h1><pre>{output}</pre></body></html>".encode())

        elif self.path.startswith("/files"):
            # VULNERABILITY: Directory listing
            try:
                path = self.path.split("?", 1)[1] if "?" in self.path else "."
                files = os.listdir(path)
                file_list = "<br>".join([f'<a href="/file?path={path}/{f}">{f}</a>' for f in files])
            except Exception as e:
                file_list = f"Error: {str(e)}"

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Files in {path}</h1>{file_list}</body></html>".encode())

        elif self.path.startswith("/file"):
            # VULNERABILITY: File reading with path traversal
            try:
                path = self.path.split("path=", 1)[1] if "path=" in self.path else "test.txt"
                with open(path, 'r') as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading file: {str(e)}"

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>File: {path}</h1><pre>{content}</pre></body></html>".encode())

        elif self.path == "/env":
            # VULNERABILITY: Environment disclosure
            env_vars = "<br>".join([f"{k}={v}" for k, v in os.environ.items()])
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Environment Variables</h1><pre>{env_vars}</pre></body></html>".encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>404 Not Found</h1></body></html>")

    def log_message(self, format, *args):
        """Override logging to be less verbose"""
        return

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

def register_routes(app, port_info=""):
    """Register all vulnerable routes for a Flask app"""

    @app.route('/')
    def index():
        return f'''
        <h1>Vulnerable Test Application {port_info}</h1>
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

# Register routes for each Flask app
register_routes(app_http, "(HTTP - Port 8080)")
register_routes(app_https, "(HTTPS - Port 8443)")
register_routes(app_alt, "(Alternative - Port 3000)")



def run_services():
    """Start all vulnerable services"""

    # Start TCP server in a thread
    tcp_server = VulnerableTCPServer(port=9000)
    tcp_thread = threading.Thread(target=tcp_server.start, daemon=True)
    tcp_thread.start()

    # Start alternative HTTP server in a thread
    def run_alt_http():
        try:
            with socketserver.TCPServer(("", 3000), VulnerableHTTPRequestHandler) as httpd:
                print("Alternative HTTP Server started on port 3000")
                httpd.serve_forever()
        except Exception as e:
            print(f"Alternative HTTP Server error: {e}")

    alt_http_thread = threading.Thread(target=run_alt_http, daemon=True)
    alt_http_thread.start()

    # Start Flask apps
    from werkzeug.serving import make_server

    # HTTP Flask app (port 8080)
    http_server = make_server('0.0.0.0', 8080, app_http, threaded=True)
    http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    http_thread.start()
    print("HTTP Flask Server started on port 8080")

    # HTTPS Flask app (port 8443) - with self-signed certificate
    try:
        # Generate self-signed certificate for HTTPS
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime

        # Generate key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Test"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Test"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=10)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())

        # Write certificate and key to files
        with open('cert.pem', 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open('key.pem', 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Start HTTPS server
        https_server = make_server('0.0.0.0', 8443, app_https,
                                   threaded=True,
                                   ssl_context=('cert.pem', 'key.pem'))
        https_thread = threading.Thread(target=https_server.serve_forever, daemon=True)
        https_thread.start()
        print("HTTPS Flask Server started on port 8443 (self-signed certificate)")

    except ImportError:
        print("cryptography library not available, skipping HTTPS server")
        https_thread = None
    except Exception as e:
        print(f"HTTPS server error: {e}")
        https_thread = None

    return {
        'tcp_server': tcp_server,
        'http_server': http_server,
        'https_server': https_server if 'https_server' in locals() else None,
        'alt_http_thread': alt_http_thread,
        'threads': [tcp_thread, http_thread, alt_http_thread] + ([https_thread] if https_thread else [])
    }

if __name__ == '__main__':
    import ipaddress

    print("Starting Multi-Service Vulnerable Application...")
    print("Available services:")
    print("  HTTP Flask App (port 8080) - Web vulnerabilities")
    print("  HTTPS Flask App (port 8443) - SSL-enabled web vulnerabilities")
    print("  TCP Server (port 9000) - Command execution and file access")
    print("  Alternative HTTP Server (port 3000) - Simple HTTP server")
    print("")
    print("Vulnerabilities available on each service:")
    print("  - SQL Injection in login forms")
    print("  - XSS in search functionality")
    print("  - Command Injection in system endpoints")
    print("  - Directory Traversal in file viewers")
    print("  - Information disclosure")
    print("  - TCP service vulnerabilities")
    print("")

    # Start all services
    servers = run_services()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        # Cleanup will happen automatically due to daemon threads
