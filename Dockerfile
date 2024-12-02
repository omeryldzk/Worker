# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the service account key file into the container
COPY service_account.json /app/service_account.json

# Set the environment variable for Google Cloud credentials
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service_account.json"

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
CMD ["python", "cloud.py"]