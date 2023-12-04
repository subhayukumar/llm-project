# Use Python311
FROM python:3.11

# Copy requirements.txt to the docker image and install packages
COPY requirements.txt /

RUN pip install -r requirements.txt

# Set the WORKDIR to be the folder
COPY . /app

ENV PORT 8080

# Expose port 5000
EXPOSE $PORT

WORKDIR /app

# Use gunicorn as the entrypoint
CMD exec gunicorn --bind :$PORT main_v1:app --workers 1 --threads 1 --timeout 60
