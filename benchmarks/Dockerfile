FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY . .
RUN poetry install

COPY benchmarks/run_benchmarks.sh /app/benchmarks/
RUN chmod +x /app/benchmarks/run_benchmarks.sh

CMD ["bash", "/app/benchmarks/run_benchmarks.sh"]
