FROM python:3.12.0-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --with app

COPY ./app/src ./src
COPY ./app/main.py ./main.py
COPY ./app/config.yaml .
COPY ./.dvc .
COPY .git .git
COPY ./models ./models

EXPOSE 8080

CMD ["python", "main.py"]