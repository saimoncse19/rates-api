FROM python:3.10
ENV PYTHONUNBUFFERED=true

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get upgrade -y
RUN apt-get install curl -y

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && chmod 755 ${POETRY_HOME}/bin/poetry

WORKDIR /rates-api

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install
COPY ./src ./src