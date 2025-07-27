# Use an official Python runtime as a parent image, specifying the platform for compatibility.
FROM --platform=linux/amd64 python:3.9-slim

# Set the working directory inside the container to /app.
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching.
# This layer will only be rebuilt if the dependencies change.
COPY requirements.txt .

# Install the Python dependencies specified in requirements.txt.
# --no-cache-dir keeps the final image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other project files into the container's working directory.
# This is the key step that includes your Python scripts, the 'models' folder,
# and the 'nltk_data' folder, ensuring the container can run offline.
COPY . .

# Specify the command to run when the container starts.
# This will execute your main script.
CMD ["python", "main_1b.py"]
