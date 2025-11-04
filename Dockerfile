FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    openjdk-11-jdk \
    nmap \
    nikto \
    sqlmap \
    tcpdump \
    tshark \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install OWASP ZAP
RUN wget https://github.com/zaproxy/zaproxy/releases/download/v2.12.0/ZAP_2.12.0_Linux.tar.gz \
    && tar -xzf ZAP_2.12.0_Linux.tar.gz \
    && mv ZAP_2.12.0 /opt/zap \
    && ln -s /opt/zap/zap.sh /usr/local/bin/zap.sh \
    && rm ZAP_2.12.0_Linux.tar.gz

# Install Metasploit Framework
RUN curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall \
    && chmod 755 msfinstall \
    && ./msfinstall \
    && rm msfinstall

# Install additional tools
RUN apt-get update && apt-get install -y \
    gobuster \
    ffuf \
    nuclei \
    arjun \
    && rm -rf /var/lib/apt/lists/*

# Install XSStrike
RUN git clone https://github.com/s0md3v/XSStrike.git /opt/xsstrike \
    && cd /opt/xsstrike \
    && pip install -r requirements.txt

# Install Jaeles
RUN wget https://github.com/jaeles-project/jaeles/releases/download/v0.17.1/jaeles_0.17.1_linux_amd64.tar.gz \
    && tar -xzf jaeles_0.17.1_linux_amd64.tar.gz \
    && mv jaeles /usr/local/bin/ \
    && rm jaeles_0.17.1_linux_amd64.tar.gz

# Set up application
WORKDIR /app
COPY . /app

# Create non-root user
RUN useradd -m -s /bin/bash scanner && chown -R scanner:scanner /app
USER scanner

EXPOSE 5000

CMD ["python", "main.py", "--api"]
