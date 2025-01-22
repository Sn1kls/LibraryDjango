FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock /app/

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install
