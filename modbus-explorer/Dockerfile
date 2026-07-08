FROM ghcr.io/home-assistant/base:latest

# Install Python and dependencies
RUN apk add --no-cache python3 py3-pip

# Create app directory
WORKDIR /app

# Copy application files
COPY rootfs/app /app

# Install Python packages
RUN pip3 install --no-cache-dir --break-system-packages \
    flask==3.0.0 \
    pymodbus==3.6.3 \
    werkzeug==3.0.1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python3", "/app/main.py"]
