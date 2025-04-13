FROM python:3.12-slim

WORKDIR /app

# Copy dependencies first for better caching
COPY pyproject.toml poetry.lock* ./

# Install Poetry
RUN pip install poetry 

RUN poetry install --no-root

# Copy the rest of the application
COPY bot.py .

# Run the bot using Poetry
CMD ["poetry", "run", "python", "bot.py"]