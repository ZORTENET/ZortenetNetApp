FROM python:3.8-slim-buster

WORKDIR /zortenet_netapp

COPY requirements.txt requirements.txt
RUN apt update -y
RUN apt install jq -y
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN mkdir capif_onboarding
COPY src/api.py /zortenet_netapp/api.py
COPY src/netapp_utils.py /zortenet_netapp/netapp_utils.py
COPY src/prepare.sh /zortenet_netapp/prepare.sh
COPY src/capif_registration_template.json /zortenet_netapp/capif_registration_template.json
CMD ["sh", "/zortenet_netapp/prepare.sh"]