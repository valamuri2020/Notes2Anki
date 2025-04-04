# Single-stage build for faster deployment
FROM python:3.11-slim

# Install poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /app/

# Configure poetry to create the virtualenv inside the project directory
RUN poetry config virtualenvs.in-project true && \
    poetry install --without dev --no-root --compile && \
    poetry run docling-tools models download

# Copy application code
COPY main.py config.py /app/
COPY services/ /app/services/

# Create directory for temporary files
RUN mkdir -p /app/tmp

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]