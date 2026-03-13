# Use the official, lightweight Python 3.14 image (match your local version)
# Note: If 3.14-slim isn't fully supported by your packages yet, use python:3.12-slim
FROM python:3.12-slim

# Prevent Python from writing .pyc files and force stdout/stderr to stream instantly
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Set the working directory inside the container
WORKDIR /app

# Copy just the requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port that Cloud Run expects
EXPOSE 8080

# Command to start the FastAPI server using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]