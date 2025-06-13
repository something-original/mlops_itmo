FROM python:3.12.0-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libssl-dev=3.0.11-1~deb12u2 \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml .
COPY .dvc .dvc

# Install dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --with app

# Copy application code
COPY ./app .

EXPOSE 8080

ENV PATH="/root/.local/bin:${PATH}"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
