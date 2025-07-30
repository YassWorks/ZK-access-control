FROM python:3.13-alpine

# no pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# no buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /pyzk_api

RUN apk add --no-cache \
    build-base \
    && rm -rf /var/cache/apk/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

COPY . .

# Create logs directory with proper permissions
RUN mkdir -p /tmp/logs && \
    chown -R appuser:appgroup /tmp/logs && \
    chown -R appuser:appgroup /pyzk_api

USER appuser

EXPOSE 9000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]