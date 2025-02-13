# Build stage
FROM python:3.11-slim as builder

# Install poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Configure poetry to create the virtualenv inside the project directory
RUN poetry config virtualenvs.in-project true

# Install dependencies
RUN poetry install --no-dev --no-root

# Development stage
FROM python:3.11-slim as development

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/poetry.lock /app/poetry.lock
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app/

# Create directory for temporary files
RUN mkdir -p /app/tmp

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application with hot reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python:3.11-slim as production

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/poetry.lock /app/poetry.lock
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app/

# Create directory for temporary files
RUN mkdir -p /app/tmp

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]