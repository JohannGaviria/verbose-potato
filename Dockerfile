ARG PYTHON_VERSION=3.12-slim
ARG POETRY_VERSION=2.3.4


FROM python:${PYTHON_VERSION} AS base
ARG POETRY_VERSION

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false
ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY --chmod=755 entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]


FROM base AS development

RUN poetry install --no-root --with dev
COPY . .

EXPOSE 8000
CMD ["dev"]


FROM base AS testing

RUN poetry install --no-root --with test
COPY . .

CMD ["test"]


FROM base AS production

RUN poetry install --no-root --with prod
COPY src ./src

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["prod"]
