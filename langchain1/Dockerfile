FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../pyproject.toml ../uv.lock* ./

# Install uv and dependencies
RUN pip install uv
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY . /app/langchain1/
COPY ../chatbot /app/chatbot/
COPY ../rag /app/rag/
COPY ../mcp_weather /app/mcp_weather/

# Create directories
RUN mkdir -p /app/data /app/logs

# Expose ports
EXPOSE 8002 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the production server
CMD ["python", "-m", "uvicorn", "langchain1.production_server:app", "--host", "0.0.0.0", "--port", "8002"]
