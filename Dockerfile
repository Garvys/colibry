#Using python
FROM python:3.9-slim
# Using Layered approach for the installation of requirements
COPY requirements.txt /app/requirements.txt
COPY calibre-python /app/calibre-python

WORKDIR /app/
RUN pip install -r requirements.txt

COPY dashboard /app/dashboard

WORKDIR /app/dashboard
EXPOSE 8050
#Running your APP and doing some PORT Forwarding
# CMD gunicorn -b 0.0.0.0:80 app:server
CMD ["python","app.py"]