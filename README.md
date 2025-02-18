# Fashion Store Backend Application

## Overview
This backend application is designed for an e-commerce platform that supports user authentication, product management, shopping cart, and order processing. It consists of various modules to manage users, products, carts, and orders. This platform allows users to create accounts, add products to their carts, place orders, and view their order history. The backend is built with Django, Django REST framework (DRF), PyJWT and utilizes a PostgreSQL database.


## Features
- `User Management`: Users can register, log in, and manage their profile.
- `Product Management`: Admins can add, update, and remove products.
- `Cart Management`: Users can add/remove products to/from their cart.
- `Order Management`: Users can create and view orders. Admins can also view order data.
- `Security`: Authenticated access using JWT tokens.

## Project Structure
### Apps
1. Users:

    - Handles user registration, login, and profile management.
    - Uses JWT authentication for secure access.
    - Admin can also access user records

2. Products:

    - Manages product listings, including CRUD (Create, Read, Update, Delete) operations.
    - Admin can publish/unpublish products.

3. Cart:

    - Users can add/remove products to/from their cart.
    - Cart items track the product quantity and price.

4. Orders:

    - Users can place orders based on the products in their cart.
    - Tracks order items and their quantities.
    - Order total is calculated dynamically.
    - Admin can access order data

### Models
The primary models include:

- User (from Django's AbstractUser)
- Product: Represents items for sale in the store.
- Cart & CartItem: Represents a shopping cart with associated products.
- Order & OrderItem: Represents customer orders and the individual items within those orders.
- UUIDPrimaryKey: All primary keys in this application are UUIDs, ensuring global uniqueness.
- Decimal Fields: Used to represent prices with two decimal places for accuracy.

### Scripts
This project includes a custom management script to aid in project setup and administration.

- `create_admin.py`:
This script is used to create a superuser with all privileges. It is useful as it will be the first user in the application, which you can then use to create additional admin users.


## Project Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/faruqt/fashion-store.git

2. Create the Environment Variables File:
Create and copy the provided sample file to `.env`
```bash
cp env.sample .env
```
Edit the `.env` file to configure your environment-specific variables as explained below.

3. Generate a secret key:
Generate a new secret key and update the `APP_SECRET_KEY` variable in your `.env` file with it:
```bash
python3 -c 'import secrets; print(secrets.token_hex())'
```

## Virtual Environment Setup

1.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Database Setup (PostgreSQL) : Execute the following instructions to setup your database locally

    - Login to PostgreSQL as a superuser
    ```bash
    psql -U postgres
    ```

    - Create database and user
    ```bash
    CREATE DATABASE fashion_store_db;
    CREATE USER fashion_store_db_user WITH PASSWORD 'fashion_store_db_password';
    ```

    - Set the user as the database owner
    ```bash
    ALTER DATABASE fashion_store_db OWNER TO fashion_store_db_user;
    ```

    - Exit psql
    ```bash
    \q
    ```

    - Update your `.env` file accordingly with the required database credentials.

4. Run migrations to set up the database:

    ```bash
    python manage.py migrate
    ```

5. Create a superuser: Run the following command to create the first superuser with all privileges. This user can be used to create additional admin users.

    ```bash
    python scripts/create_admin.py
    ```

6. Start the development server:

    ```bash
    python manage.py runserver
    ```

7. Access the Application:
The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000). This URL will serve the application's web interface.

## Docker Setup
### Local Setup
1. Build and Run the Docker Image:
Ensure Docker and Docker Compose are installed on your machine. Use the following command to build and start the application container:
```bash
docker-compose up
```

This will start the `backend` service, which includes the main application logic. It will build the Docker image for the `backend` service (if not already built) and then run it.

2. Access the Application:
The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000). This URL will serve the application's web interface.

### Production Setup
For a production environment, use the following steps to setup the environment:
1. Build and Run the Docker Image:
In a production environment, you may want to use a different configuration file. Run the following command to build and start the production container:
```bash
docker-compose -f docker-compose.prod.yml up
```
- `-f docker-compose.prod.yml`: This flag specifies the use of the `docker-compose.prod.yml` file, which contains production-specific configurations.

### Notes on Running Docker
- `Environment Variables`: Make sure to set the appropriate environment variables in your `.env` file before running the containers. This file should be configured based on the environment you are working in (development, staging, production).
- `Automatic Reloading`: Code changes are automatically reflected due to volume mounts.
- `Service Restart`: To restart the service if you make changes to the configuration, run the commands below:
```bash
docker-compose down
docker-compose up
```
- `Stopping Containers`: To stop the running containers, use `docker-compose down`. This will stop and remove the containers but keep the images.

## Testing
### Running Tests
To ensure the quality of the application, we have tests written for each app. The project is set up to use pytest as the testing framework.

1. Run Tests:
Run the automated test suite. using the following command:
```
bash run-tests.sh
```
This will execute a script that automatically discovers and runs all tests in the app folders using pytest.

## Additional Notes
- Ensure you have Docker Compose installed. If not, follow [Docker's installation guide](https://docs.docker.com/get-docker/) to set it up.
- Adjust Dockerfile or Compose configurations as needed based on your environment and requirements.
- For any issues or contributions, please contact the maintainer.