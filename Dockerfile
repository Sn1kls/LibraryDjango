FROM python:3.13.0

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock* /usr/src/app/

RUN pip install poetry

RUN poetry install

COPY . .