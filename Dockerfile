FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 10001 appuser

# Copy application
COPY --chown=appuser:appuser . .

# Make scripts executable
RUN chmod +x /app/start-up.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/app/start-up.sh"]
