# Use an official Python runtime as a parent image
# Explicitly set the platform to linux/amd64 for compatibility
FROM --platform=linux/amd64 python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir ensures that we don't store the download cache, keeping the image size smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY main.py .
COPY utils.py .

# Create the input and output directories
# These directories will be used for mounting volumes during runtime
RUN mkdir -p /app/input /app/output

# Specify the command to run on container startup
# This will execute the main.py script to process the PDFs
CMD ["python", "main.py"]
