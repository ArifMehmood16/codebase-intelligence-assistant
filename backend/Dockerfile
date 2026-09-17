FROM python:3.14-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml requirements.lock ./
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.lock \
    && pip install --no-cache-dir --no-deps .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn codebase_assistant.main:app --host 0.0.0.0 --port 8000"]
