FROM python:3.8-alpine

RUN pip install blinkpy

WORKDIR /app

COPY ./blink.py /app/

CMD ["python", "blink.py"]