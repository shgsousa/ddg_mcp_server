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

# Copy the application code and example .env file
COPY main.py .
COPY .env.example .

# Set environment variables with default values
ENV OPENAI_API_URL="https://api.openai.com/v1"
ENV ACCESS_TOKEN=""

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application with proper host binding
ENTRYPOINT ["python", "main.py"]