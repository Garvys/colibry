FROM python:3.9-alpine as colibry

ENV COLIBRY_LIBRARY_PATH="/app/library"

COPY requirements.txt /app/requirements.txt
COPY calibre-python /app/calibre-python

WORKDIR /app/
RUN pip install -r requirements.txt

COPY dashboard /app/dashboard

WORKDIR /app/dashboard
EXPOSE 8050
CMD ["gunicorn", "-b", "0.0.0.0:8050", "--reload", "app:server"]
