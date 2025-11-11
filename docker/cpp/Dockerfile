# CompileMate C++ Execution Environment
FROM gcc:latest

# Install build essentials
RUN apt-get update && apt-get install -y \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1001 coderunner

# Set working directory
WORKDIR /app

# Switch to non-root user
USER coderunner

# Default command
CMD ["g++"]

