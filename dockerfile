FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


COPY reqs.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r reqs.txt

COPY . .

CMD ["python","main.py"]