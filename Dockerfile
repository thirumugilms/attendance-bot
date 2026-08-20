# Use the official lightweight Python image
FROM python:3.11-slim

# Install system dependencies extending to those strictly required by Playwright/Chromium
RUN apt-get update && apt-get install -y \
    curl \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements and gunicorn (for production web serving)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Install playwright chromium explicitly including missing OS deps it finds
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy app files
COPY . .

# Ensure start script is executable
RUN chmod +x start.sh

# Environment variables
ENV HEADLESS=True
ENV PORT=5000

# Start script handles both the background scheduler process and the Flask UI
CMD ["./start.sh"]
