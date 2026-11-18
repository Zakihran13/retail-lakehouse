# Use an official Python runtime as a parent image
FROM python:3.12-slim AS builder

# Install uv using the official installer script
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation and disable uv sync prompts
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install dependencies first (leveraging Docker layer caching)
# Copy dependency specification files
COPY pyproject.toml uv.lock ./

# Install project dependencies without the project itself yet
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . /app

# Install the project itself now
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# --- Final runtime image ---
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY --from=builder /app /app

# Place the virtual environment's binaries on the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run your application (adjust command as needed)
CMD ["python", "main.py"]