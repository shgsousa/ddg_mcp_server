# Use Python 3.12 as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --no-cache --system -r requirements.txt

# Copy the application code
COPY main.py .

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application with proper host binding
ENTRYPOINT ["python", "main.py"]