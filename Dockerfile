# Use a small official Python base image
FROM python:3.11.8-slim

# Install system deps (example: ffmpeg, curl, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        ffmpeg \
        vim \
        git \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# -------- Install BBDown binary --------
# Replace the URL below with the latest Linux x64 BBDown release URL
RUN curl -L "https://github.com/nilaoda/BBDown/releases/download/1.6.3/BBDown_1.6.3_20240814_linux-x64.zip" -o /usr/local/bin/BBDown && \
    chmod +x /usr/local/bin/BBDown

# -------- Set up Python environment --------
WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Make Python output unbuffered (logs appear immediately)
ENV PYTHONUNBUFFERED=1

# Default entrypoint: run your script
CMD ["bash", "-lc", "sleep infinity"]
