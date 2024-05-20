# FROM python:3.9-slim as calibre

# # Install calibre
# RUN apt-get update && \
#     apt-get install libegl1 libopengl0 libxcb-cursor0 wget xz-utils libfontconfig libxkbcommon-x11-0 python3-pyqt5 -y
# RUN  wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin version=7.10.0 install_dir=/opt isolated=y  && \
#     apt-get remove wget xz-utils libfontconfig -y && \
#     apt-get autoremove -y && apt-get clean
# RUN ./opt/calibre/calibredb --version

# RUN rm -rf /opt/calibre/translations
# RUN rm -rf /opt/calibre/lib/libQt6WebEngineCore.so.6


FROM python:3.9-slim as calibredb

# RUN apt-get update && \
#     apt-get install libegl1 libfontconfig libxkbcommon-x11-0 libglx-dev libopengl0 -y && \
#     apt-get clean

# COPY --from=calibre /opt/calibre /opt/calibre

# ENV PATH "$PATH:/opt/calibre"

# RUN calibredb --version

FROM calibredb as colibry

ENV COLIBRY_LIBRARY_PATH="/app/library"

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