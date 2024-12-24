FROM python:3.13.0

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip \
    && pip install poetry

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock* /usr/src/app/

RUN poetry config virtualenvs.create false \
    && poetry install

COPY . /usr/src/app/