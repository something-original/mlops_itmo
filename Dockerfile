FROM python:3.12.0-slim
WORKDIR /app
COPY ./app .
COPY pyproject.toml .

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --with app
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
