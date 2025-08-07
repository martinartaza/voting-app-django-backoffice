FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

EXPOSE 8080

# Use the entrypoint script instead of direct gunicorn
CMD ["./entrypoint.sh"]