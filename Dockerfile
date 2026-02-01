FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 
WORKDIR /app

# system deps for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# copy requirements first for caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /app

EXPOSE 8080

# Use gunicorn to serve the Flask app defined in app.py as `app`
CMD ["gunicorn", "-w", "2", "--timeout", "120", "-b", "0.0.0.0:8080", "app:app"]
