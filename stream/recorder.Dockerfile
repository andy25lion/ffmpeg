FROM python:3.8-alpine

RUN apk add  --no-cache ffmpeg

WORKDIR /app

COPY ./stream.py /app/

CMD ["python", "stream.py"]