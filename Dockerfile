FROM python:3.11.5

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
