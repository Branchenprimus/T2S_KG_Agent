# Start from slim Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc wget curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt \
    && pip install watchgod  # <- ADD THIS for auto-reloading!

# Copy application code
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# No need for start.sh anymore — directly use uvicorn with reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
