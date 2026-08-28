ARG PYTHON_IMAGE=python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7

FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --gid 10001 portfolio \
    && useradd --uid 10001 --gid portfolio --create-home --shell /usr/sbin/nologin portfolio

WORKDIR /app

COPY pyproject.toml README.md requirements.lock requirements-dev.lock ./
COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic
COPY fixtures ./fixtures

RUN python -m pip install --requirement requirements.lock \
    && python -m pip install --no-deps --editable . \
    && mkdir -p /app/var \
    && chown portfolio:portfolio /app/var

USER portfolio

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2).read()"]

CMD ["portfolio-agent", "serve", "--docker-local", "--port", "8000"]


FROM runtime AS test

USER root
COPY --chown=portfolio:portfolio tests ./tests
COPY --chown=portfolio:portfolio docs ./docs
COPY --chown=portfolio:portfolio .agents/runs/uk-literature-public-evidence-upgrade.md \
    ./.agents/runs/uk-literature-public-evidence-upgrade.md
RUN python -m pip install --requirement requirements-dev.lock \
    && python -m pip install --no-deps --editable '.[dev]'
USER portfolio

WORKDIR /tmp
CMD ["python", "-m", "pytest", "/app/tests", "-o", "cache_dir=/tmp/.pytest_cache", "--cov=portfolio_agent", "--cov-report=term-missing"]
