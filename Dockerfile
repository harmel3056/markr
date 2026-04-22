FROM python:3.12-slim

WORKDIR /app
RUN mkdir -p /app && chmod -R 777 /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4567"]