# Use the official Microsoft Playwright image which has Chromium and all OS dependencies pre-installed!
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install Python requirements and gunicorn (for production web serving)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Install playwright chromium (The OS dependencies are already baked into the image)
RUN playwright install chromium

# Copy app files
COPY . .

# Ensure start script is executable
RUN chmod +x start.sh

# Environment variables
ENV HEADLESS=True
ENV PORT=5000

# Start script handles both the background scheduler process and the Flask UI
CMD ["./start.sh"]
