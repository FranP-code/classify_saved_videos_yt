FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (no Ollama needed - using separate container)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    curl \
    wget \
    git \
    sudo \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    firefox \
    python3-tk \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create user vscode
RUN useradd -m -s /bin/bash vscode && \
    usermod -aG sudo vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /workspace
RUN chown vscode:vscode /workspace

USER vscode

# Install pip
RUN python3 -m pip install --user --upgrade pip

ENV PATH="/home/vscode/.local/bin:$PATH"
ENV DISPLAY=:1

# Copy startup script and make it executable
COPY --chown=vscode:vscode start-services.sh /home/vscode/start-services.sh
USER root
RUN chmod +x /home/vscode/start-services.sh
USER vscode

CMD ["/bin/bash", "/home/vscode/start-services.sh"]
