#!/bin/bash

# Print a message indicating that the script is starting
echo "Starting build process..."

# Create a virtual environment
echo "Creating virtual environment..."
python -m venv myenv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment. Exiting."
    exit 1
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source myenv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment. Exiting."
    exit 1
fi

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Exiting."
    exit 1
fi

# Run collectstatic command
echo "Collecting static files..."
python manage.py collectstatic
if [ $? -ne 0 ]; then
    echo "Failed to collect static files. Exiting."
    exit 1
fi

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

# Print a message indicating that the script has finished successfully
echo "Build process completed successfully."
