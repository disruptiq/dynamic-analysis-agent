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
    golang-go \
    ruby \
    ruby-dev \
    gem \
    && rm -rf /var/lib/apt/lists/*

# Setup Go environment
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/root/go
ENV GOROOT=/usr/local/go
ENV PATH=$PATH:$GOPATH/bin

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

# Install Kali Linux tools
RUN apt-get update && apt-get install -y \
    hydra \
    wpscan \
    joomlavs \
    dnsrecon \
    enum4linux \
    bettercap \
    aircrack-ng \
    john \
    hashcat \
    crackmapexec \
    proxychains \
    sqlninja \
    xsser \
    patator \
    dotdotpwn \
    && rm -rf /var/lib/apt/lists/*

# Install Evil-WinRM
RUN gem install evil-winrm

# Install Chisel
RUN wget https://github.com/jpillora/chisel/releases/download/v1.7.7/chisel_1.7.7_linux_amd64.gz \
    && gunzip chisel_1.7.7_linux_amd64.gz \
    && chmod +x chisel \
    && mv chisel /usr/local/bin/

# Install Commix
RUN git clone https://github.com/commixproject/commix.git /opt/commix \
    && ln -s /opt/commix/commix.py /usr/local/bin/commix

# Install Tplmap
RUN git clone https://github.com/epinna/tplmap.git /opt/tplmap \
    && cd /opt/tplmap \
    && pip install -r requirements.txt \
    && ln -s /opt/tplmap/tplmap.py /usr/local/bin/tplmap

# Install Recon-ng
RUN git clone https://github.com/lanmaster53/recon-ng.git /opt/recon-ng \
    && cd /opt/recon-ng \
    && pip install -r REQUIREMENTS \
    && ln -s /opt/recon-ng/recon-ng /usr/local/bin/recon-ng

# Install TheHarvester
RUN git clone https://github.com/laramies/theHarvester.git /opt/theharvester \
    && cd /opt/theharvester \
    && pip install -r requirements.txt \
    && ln -s /opt/theharvester/theHarvester.py /usr/local/bin/theHarvester

# Install Amass
RUN wget https://github.com/OWASP/Amass/releases/download/v3.21.2/amass_linux_amd64.zip \
    && unzip amass_linux_amd64.zip \
    && mv amass_linux_amd64/amass /usr/local/bin/ \
    && rm -rf amass_linux_amd64*

# Install Sublist3r
RUN git clone https://github.com/aboul3la/Sublist3r.git /opt/sublist3r \
    && cd /opt/sublist3r \
    && pip install -r requirements.txt \
    && ln -s /opt/sublist3r/sublist3r.py /usr/local/bin/sublist3r

# Install Go tools
RUN go install github.com/tomnomnom/assetfinder@latest \
    && go install github.com/tomnomnom/httprobe@latest \
    && go install github.com/tomnomnom/gf@latest \
    && go install github.com/tomnomnom/qsreplace@latest \
    && go install github.com/Montferret/ferret@latest \
    && cp ~/go/bin/* /usr/local/bin/

# Install gf patterns
RUN git clone https://github.com/1ndianl33t/Gf-Patterns.git ~/.gf

# Install Responder
RUN git clone https://github.com/lgandx/Responder.git /opt/responder \
    && ln -s /opt/responder/Responder.py /usr/local/bin/responder

# Install Joomlavs
RUN git clone https://github.com/rastating/joomlavs.git /opt/joomlavs \
    && cd /opt/joomlavs \
    && chmod +x joomlavs.rb \
    && ln -s /opt/joomlavs/joomlavs.rb /usr/local/bin/joomlavs

# Install Python Kali tools
RUN pip install \
    dnsrecon \
    responder \
    crackmapexec \
    commix \
    tplmap \
    xsser \
    patator \
    recon-ng \
    theharvester \
    sublist3r \
    dotdotpwn \
    shodan

# Set up application
WORKDIR /app
COPY . /app

# Create non-root user
RUN useradd -m -s /bin/bash scanner && chown -R scanner:scanner /app
USER scanner

EXPOSE 5000

CMD ["python", "main.py", "--api"]
