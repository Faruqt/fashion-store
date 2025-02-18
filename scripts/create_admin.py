import os
import sys
import django

# Add the project directory to sys.path to allow for correct module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Set up the Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fashionstore.settings")
django.setup()

# Now you can import your models
from users.models import Users

try:
    # check if the superuser already exists
    if Users.objects.filter(email="admin@example.com").exists():
        print("Superuser already exists.")
        sys.exit()

    Users.objects.create_super_user(
        email="admin@example.com", password="password123", first_name="Admin"
    )
    print("Superuser created successfully.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
