FROM python:3.9-slim AS builder

# Install build dependencies
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

ARG POETRY_VERSION=1.1.13

# Disable stdout/stderr buggering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

# Disable some obvious pip functionality
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_PATH=/venvs

# Install Poetry
RUN pip install -U pip wheel setuptools && \
  pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

#
# dev-runtime
#

FROM builder AS dev-runtime

RUN poetry install

COPY dev/entrypoint.sh /app/dev/
ENTRYPOINT [ "dev/entrypoint.sh" ]

EXPOSE 8000/tcp

CMD ["poetry", "run", "gunicorn", "iscc_registry.asgi:application", "--bind=0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "--reload"]

#
# prod-runtime
#

FROM builder AS prod-runtime

RUN poetry install --no-dev --remove-untracked

COPY . /app/
ENTRYPOINT [ "dev/entrypoint.sh" ]

EXPOSE 8000/tcp

CMD ["poetry", "run", "gunicorn", "iscc_registry.asgi:application", "--bind=0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker"]
