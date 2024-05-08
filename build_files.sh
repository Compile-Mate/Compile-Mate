#!/bin/bash

# Print a message indicating that the script is starting
echo "Starting build process..."

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Exiting."
    exit 1
fi

# Run collectstatic command
echo "Collecting static files..."
python3.9 manage.py collectstatic
if [ $? -ne 0 ]; then
    echo "Failed to collect static files. Exiting."
    exit 1
fi

# Print a message indicating that the script has finished successfully
echo "Build process completed successfully."
