FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including Git
RUN apt-get update && apt-get install -y git && apt-get clean

# Install uv
RUN pip install uv

# Copy pyproject.toml and uv.lock
COPY pyproject.toml uv.lock ./

# Use uv to install dependencies
RUN uv sync

# Copy the application code
COPY main.py ./

# Expose the port that FastAPI will run on
EXPOSE 8000

# Use `uv run` to start Uvicorn properly
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
