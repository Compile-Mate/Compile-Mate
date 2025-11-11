# CompileMate Java Execution Environment
FROM eclipse-temurin:17-jdk-alpine

# Create non-root user for security
RUN adduser -D -u 1001 coderunner

# Set working directory
WORKDIR /app

# Switch to non-root user
USER coderunner

# Default command
CMD ["java"]

