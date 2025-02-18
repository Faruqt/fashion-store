# Here we are using a multi-stage build to reduce the size of the final image.
# The first stage is used to install the dependencies and the second stage is used to copy the installed dependencies and the application code.
# We have some packages that are required to build the dependencies, so we install them in the first stage and remove them in the same stage to reduce the size of the final image.

# Stage 1: Build Stage
FROM python:3.9.5-slim-buster AS build

ARG REQUIREMENTS_FILE=requirements.txt
# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./${REQUIREMENTS_FILE} /app/${REQUIREMENTS_FILE}

# Install build dependencies and Python dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && pip install --no-cache-dir -r ${REQUIREMENTS_FILE} \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Final Stage (Production)
FROM python:3.9.5-slim-buster

# Set the working directory
WORKDIR /app

# Copy the installed packages from the build stage
COPY --from=build /usr/local /usr/local

# Copy the application files
COPY . /app

# Run as own user (not root) for security purposes
RUN groupadd -r fashionstore && useradd --no-log-init -r -g fashionstore fashionstore

# Set environment variable to ensure logs are visible
ENV PYTHONUNBUFFERED=1

# Set the APP_ROOT environment variable
ENV APP_ROOT=/app

# Expose port 8000 for Django
EXPOSE 8000

# Set the entrypoint for the app (using gunicorn to serve the Django app)
USER fashionstore

CMD ["/bin/bash", "entrypoint.sh"]
