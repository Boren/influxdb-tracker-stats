FROM python:3.8-slim

WORKDIR /app
COPY /requirements.txt /trackerstats.yaml /trackerstats.py /app/
COPY /trackerstats /app/trackerstats
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD python /app/trackerstats.py

VOLUME /config