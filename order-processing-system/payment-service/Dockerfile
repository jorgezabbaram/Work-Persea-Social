FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Generate lock file and install dependencies
RUN poetry lock && poetry install --no-root

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run entrypoint that validates files, runs migrations and starts server
CMD ["python", "docker_entrypoint.py"]