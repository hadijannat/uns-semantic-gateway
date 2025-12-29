FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src
COPY config ./config

# Set Python path for imports
ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]
