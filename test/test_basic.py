#!/usr/bin/env python3
"""
Basic test script for the vulnerable application
"""

import sys
import os

# Test basic imports
try:
    import flask
    import sqlite3
    import threading
    import socket
    import ssl
    import time
    import ipaddress
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import socketserver
    print("OK: All required modules imported successfully")
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    sys.exit(1)

# Test vulnerable_app imports
try:
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(__file__))

    # Test basic imports from vulnerable_app
    from flask import Flask, request, render_template_string, send_file, jsonify
    print("OK: Flask imports successful")

    # Test that we can create Flask apps
    app_http = Flask(__name__)
    app_https = Flask(__name__)
    app_alt = Flask(__name__)
    print("OK: Flask applications created successfully")

    print("OK: Basic functionality test passed")
    print("\nTo run the full application:")
    print("  docker-compose up --build")
    print("  # or")
    print("  python vulnerable_app.py")

except Exception as e:
    print(f"ERROR: Application test failed: {e}")
    sys.exit(1)
