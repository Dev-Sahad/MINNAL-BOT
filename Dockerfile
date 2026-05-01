FROM python:3.11-slim

# Install FFmpeg and audio dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    libopus-dev \
    libffi-dev \
    libnacl-dev \
    libsodium-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Verify FFmpeg is installed
RUN which ffmpeg && ffmpeg -version

# Set working directory
WORKDIR /app

# Copy and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all bot files
COPY . .

# Set environment variable for unbuffered output
ENV PYTHONUNBUFFERED=1

# Expose web panel port
EXPOSE 8080

# Run the bot
CMD ["python", "start.py"]