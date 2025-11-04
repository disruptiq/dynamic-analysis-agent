FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY vulnerable_app.py .

# Create a test file for directory traversal testing
RUN echo "This is a test file for directory traversal testing." > test.txt
RUN echo "Sensitive information: API_KEY=secret123" > config.txt

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "vulnerable_app.py"]
