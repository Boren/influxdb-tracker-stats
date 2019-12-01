FROM python:3.8-slim

ENV DATA_FOLDER="/config"

WORKDIR /app
COPY /requirements.txt /trackerstats.example.yaml /trackerstats.py /app/
COPY /trackerstats /app/trackerstats
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD cp /app/trackerstats.example.yaml /config/trackerstats.example.yaml && python /app/trackerstats.py

VOLUME /config