#!/bin/bash
# Function to check if Django server is already running on port 8000
check_server_running() {
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo "Django server is already running on port 8000. Killing the process..."
        lsof -t -i :8000 | xargs kill -9
    fi
}
# Function to activate the virtual environment and run Django server
run_server() {
    # Change directory to your Django project folder
    # Load environment variables from .env file
    source .env
    # Activate the virtual environment
    source venv/bin/activate
    flake8
    python manage.py runserver
}
run_packages() {
    # Change directory to your Django project folder
    # Load environment variables from .env file
    source .env
    # Activate the virtual environment
    source venv/bin/activate
    # Install packages
    pip install -r requirements.txt
    # Freeze installed packages to requirements.txt
    pip freeze > requirements.txt
    # Run flake8
    flake8
    # Run migrations
    python manage.py migrate
}
run_tests() {
    # Change directory to your Django project folder
    # Load environment variables from .env file
    source .env
    # Activate the virtual environment
    source venv/bin/activate
    # Run flake8
    flake8
    # Run tests
    python manage.py test
}
# Function to run migrations
run_migrations() {
    # Change directory to your Django project folder
    # Load environment variables from .env file
    source .env
    # Activate the virtual environment
    source venv/bin/activate
    
    # Run flake8
    flake8

    # Run migrate
    python manage.py migrate
}
# Function to make migrations
make_migrations() {
    # Change directory to your Django project folder
    # Load environment variables from .env file
    source .env
    # Activate the virtual environment
    source venv/bin/activate
    flake8

    # Run makemigrations
    python manage.py makemigrations
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
        run_packages
        ;;
    *)
        echo "Invalid command. Usage: ./build.sh [runserver|migrate|makemigrations|install|test]"
        exit 1
        ;;
esac
