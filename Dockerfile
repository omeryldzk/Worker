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

# Pass and write the service account key during the build
ARG GOOGLE_APPLICATION_CREDENTIALS
RUN echo "$GOOGLE_APPLICATION_CREDENTIALS" > /app/service_account.json

# Set environment variables
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service_account.json"
ENV FLASK_APP=cloud.py

# Expose the port the app runs on
EXPOSE 8080

# Define the command to start Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
