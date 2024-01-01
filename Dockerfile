FROM python:3.11-alpine as builder
WORKDIR /build
COPY requirements.txt .
# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    build-base python3-dev libpq postgresql-dev gcc jpeg-dev zlib-dev libffi-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

FROM python:3.11-alpine
WORKDIR /app
# Copy necessary files
COPY --from=builder /build /app
COPY . .
# Add runtime dependencies
RUN apk add --no-cache postgresql-dev jpeg-dev && \
    rm -rf /var/cache/apk/*

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Non-root user
RUN adduser -D myuser
USER myuser

# Command to run the application
CMD ["gunicorn", "--reload", "--workers=2", "--worker-tmp-dir", "/dev/shm", "--bind=0.0.0.0:80", "--chdir", "/app/crawler", "crawler.wsgi"]
