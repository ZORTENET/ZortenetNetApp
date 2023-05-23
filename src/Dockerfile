FROM python:3.10


WORKDIR /zortenet_netapp

COPY requirements.txt requirements.txt
RUN apt update -y
RUN apt install jq -y
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY src/api.py api.py
CMD ["sh", "/zortenet_netapp/prepare.sh"]
#CMD python -u /zortenet_netapp/api.py
