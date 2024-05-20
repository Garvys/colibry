#Using python
FROM python:3.9-slim

ENV COLIBRY_LIBRARY_PATH="/app/library"

# Install calibre
RUN apt-get update && \
    apt-get install libegl1 libopengl0 libxcb-cursor0 wget xz-utils libfontconfig libxkbcommon-x11-0 python3-pyqt5 -y && \
    wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin version=7.10.0 

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