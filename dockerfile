FROM python:latest
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 80
CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--port", "80"] 