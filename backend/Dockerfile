FROM python:3.10-slim

WORKDIR /backend

RUN pip install gunicorn==21.2.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
