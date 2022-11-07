FROM python:3.8-slim-buster

WORKDIR /zortenet_netapp

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY src/api.py api.py
COPY src/emulator_utils.py emulator_utils.py
