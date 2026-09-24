FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests
RUN python -m pip install --no-cache-dir ".[test]"

CMD ["python", "-m", "pytest"]
