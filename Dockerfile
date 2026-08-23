# Stage 1: Build dependencies using uv sync
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Run uv sync to automatically create and populate the local .venv folder
RUN uv sync

# Stage 2: Production runtime image
FROM python:3.14-slim

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the local .venv folder generated in stage 1
COPY --from=builder /app/.venv /app/.venv

# Add the .venv binaries to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY . .

EXPOSE 8501

CMD ["/app/.venv/bin/python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]