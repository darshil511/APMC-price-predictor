# Use Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install OS-level dependencies required for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port
EXPOSE 5000

# Final command
CMD ["bash", "-c", "python setup_db.py && python download_data.py && python app.py"]
