#!/bin/bash

# Change to the directory where this script resides
cd "$(dirname "$0")"

# Function to check if Django server is already running on port 8000
check_server_running() {
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo "Django server is already running on port 8000. Killing the process..."
        lsof -t -i :8000 | xargs kill -9
    fi
}

# Function to activate the virtual environment
activate_virtualenv() {
    # Replace 'path/to/your/venv/bin/activate' with the path to your virtual environment activation script
    source venv/scripts/activate
}

# Function to install dependencies
install_dependencies() {
    activate_virtualenv
    pip install -r requirements.txt
}

# Function to run flake8 for linting
run_flake8() {
    activate_virtualenv
    flake8
}

# Function to run Django server
run_server() {
    activate_virtualenv
    run_flake8
    python manage.py runserver
}

# Function to run Django migrations
run_migrations() {
    activate_virtualenv
    run_flake8
    python manage.py migrate
}

# Function to generate Django migration files
make_migrations() {
    activate_virtualenv
    run_flake8
    python manage.py makemigrations
}

# Function to run Django tests
run_tests() {
    activate_virtualenv
    run_flake8
    python manage.py test
}

# Main script logic
case "$1" in
    runserver)
        check_server_running
        run_server
        ;;
    migrate)
        run_migrations
        ;;
    makemigrations)
        make_migrations
        ;;
    test)
        run_tests
        ;;
    install)
        install_dependencies
        ;;
    *)
        echo "Invalid command. Usage: ./build.sh [runserver|migrate|makemigrations|install|test]"
        exit 1
        ;;
esac
