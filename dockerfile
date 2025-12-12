# Use official Python base (multi-arch, works on Raspberry Pi and others)
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr (good for docker logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only requirements (update this if you add deps)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY ./feature_extractor_api.py .

# Expose whatever port your API serves (if applicable)
EXPOSE 5000

# Default command: run your API
CMD ["python", "feature_extractor_api.py"]
