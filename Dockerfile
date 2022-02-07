FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y \
  vim-tiny \
  binutils \
  libproj-dev \
  gdal-bin \
  python3-gdal \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
ENV PYTHONUNBUFFERED 1

CMD ["gunicorn", "--reload", "--workers=3", "--worker-tmp-dir", "/dev/shm", "--bind=0.0.0.0:80", "--chdir", "/app/crawler", "crawler.wsgi"]
