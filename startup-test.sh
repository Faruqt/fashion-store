#!/bin/bash

# handle database migrations
python manage.py makemigrations

python manage.py migrate

# Run tests
echo "Running tests..."
pytest -v
echo "Tests complete."
