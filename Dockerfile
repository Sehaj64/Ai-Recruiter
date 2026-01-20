FROM python:3.11.5-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (needed for Spacy/AI tools)
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

# Copy all your project code
COPY . .

# Expose the port your application listens on
EXPOSE 5000

# Run the main application with cloud-optimized flags
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
