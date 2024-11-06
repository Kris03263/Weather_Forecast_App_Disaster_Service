FROM python:alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENV FLASK_APP=app.py

CMD ["python3", "index.py"]