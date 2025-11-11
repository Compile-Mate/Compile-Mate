# CompileMate JavaScript Execution Environment
FROM node:18-slim

# Create non-root user for security (use different UID to avoid conflict)
RUN useradd -m -u 1001 coderunner

# Set working directory
WORKDIR /app

# Switch to non-root user
USER coderunner

# Default command
CMD ["node"]

