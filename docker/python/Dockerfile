# CompileMate Python Execution Environment
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 coderunner

# Set working directory
WORKDIR /app

# Install common Python packages (optional)
RUN pip install --no-cache-dir numpy

# Switch to non-root user
USER coderunner

# Default command
CMD ["python3"]

