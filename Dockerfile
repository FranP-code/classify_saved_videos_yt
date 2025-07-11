# Use Ubuntu 22.04 as base
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Enable universe category
RUN echo "deb http://archive.ubuntu.com/ubuntu bionic main universe" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu bionic-security main universe" >> /etc/apt/sources.list
RUN echo "deb http://archive.ubuntu.com/ubuntu bionic-updates main universe" >> /etc/apt/sources.list


# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
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
    xterm \
    firefox \
    python3-tk \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create user
RUN useradd -m -s /bin/bash user && \
    usermod -aG sudo user && \
    echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up workspace
WORKDIR /workspace
RUN chown user:user /workspace

# Switch to user
USER user

# Install Python packages
COPY requirements.txt .
RUN python3 -m pip install --user -r requirements.txt

# Set environment
ENV PATH="/home/user/.local/bin:$PATH"
ENV DISPLAY=:1

# Copy startup script
COPY docker-entrypoint.sh /home/user/
USER root
RUN chmod +x /home/user/docker-entrypoint.sh
USER user

ENTRYPOINT ["/home/user/docker-entrypoint.sh"]
