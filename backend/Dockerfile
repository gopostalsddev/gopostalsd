FROM python:3.12.10-slim-bookworm AS wheels

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY requirements.txt .
RUN python -m pip wheel --wheel-dir /wheels --requirement requirements.txt


FROM python:3.12.10-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5000

RUN groupadd --gid 10001 gopostal \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin gopostal

WORKDIR /app
COPY --from=wheels /wheels /wheels
COPY requirements.txt .
RUN python -m pip install --no-index --find-links=/wheels --requirement requirements.txt \
    && rm -rf /wheels

COPY --chown=10001:10001 . .
RUN chmod 0555 /app/deploy.sh /app/migrate.sh

USER 10001:10001

EXPOSE 5000
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=4 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health/ready', timeout=2).read()"]

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
