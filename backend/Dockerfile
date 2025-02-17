# Build stage
FROM python:3.11-slim as builder

# Install poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Configure poetry to create the virtualenv inside the project directory
RUN poetry config virtualenvs.in-project true

# Install dependencies; use compile to convert Python to bytecode upon install instead of first run
RUN poetry install --without dev --no-root --compile

# Development stage
FROM python:3.11-slim AS development

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/poetry.lock /app/poetry.lock
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Set working directory
WORKDIR /app

# Copy application code
COPY main.py /app/
COPY config.py /app/
COPY backend/services/validator.py /app/services/
COPY backend/services/file_processor.py /app/services/
COPY backend/services/anki_generator.py /app/services/
COPY backend/services/card_creator.py /app/services/

# Create directory for temporary files
RUN mkdir -p /app/tmp

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Download models
RUN docling-tools models download

# Expose port
EXPOSE 8000

# Run the application with hot reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python:3.11-slim AS production

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/poetry.lock /app/poetry.lock
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Set working directory
WORKDIR /app

# Copy application code
COPY main.py /app/
COPY config.py /app/
COPY ./services/ /app/

# Create directory for temporary files
RUN mkdir -p /app/tmp

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Download models
RUN docling-tools models download

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]