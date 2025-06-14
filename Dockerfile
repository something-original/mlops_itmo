FROM python:3.12.0-slim

WORKDIR /app
COPY ./app ./app
COPY pyproject.toml .
COPY .dvc .
COPY ./models ./models

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --with app
EXPOSE 8080

CMD ["python", "app/main.py"]