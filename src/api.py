import time
from flask import Flask, request, jsonify
import requests
import evolved5g
import os
import subprocess
import json
from queue import Queue
from threading import Thread
import datetime

from evolved5g.sdk import LocationSubscriber ,CAPIFInvokerConnector
from evolved5g.swagger_client.rest import ApiException
from evolved5g.swagger_client import LoginApi, User ,Configuration ,ApiClient
from evolved5g.swagger_client.models import Token


policy_db={}

vapp_db={
    'host_name':"",
    'port':0,
    'token':0
}

q = Queue(maxsize = 1)


network_app_id = "Zortenetapp"
nef_url = "https://{}:{}".format(os.getenv('NEF_IP'), os.environ.get('NEF_PORT'))
nef_callback = "http://{}:{}/netAppCallback".format(os.getenv('NEF_CALLBACK_IP'), os.environ.get('NEF_CALLBACK_PORT'))
nef_user = os.getenv('NEF_USER')
nef_pass = os.environ.get('NEF_PASS')
capif_host = os.getenv('CAPIF_HOSTNAME')
capif_https_port = os.environ.get('CAPIF_PORT_HTTPS')
folder_path_for_certificates_and_capif_api_key = os.environ.get('PATH_TO_CERTS')


configuration = Configuration()
configuration.host = nef_url
configuration.verify_ssl = False
api_client = ApiClient(configuration=configuration)
api_client.select_header_content_type(["application/x-www-form-urlencoded"])
api = LoginApi(api_client)
token = api.login_access_token_api_v1_login_access_token_post("", nef_user, nef_pass, "", "", "")

nef_token = token.access_token


app = Flask(__name__)



@app.route('/', methods=["GET", "POST"])
def index():
    return "hi"



@app.route('/subscription', methods=["GET","POST"])
def vappRegister_capif():
    data = request.json
    external_id=data['id']
    times=data['num_of_reports']
    expire_time=data['exp_time']

    location_subscriber = LocationSubscriber(nef_url, nef_token, folder_path_for_certificates_and_capif_api_key, capif_host, capif_https_port)


    subscription = location_subscriber.create_subscription(
        netapp_id=network_app_id,
        external_id=external_id,
        notification_destination=nef_callback,
        maximum_number_of_reports=times,
        monitor_expire_time=expire_time
    )
    monitoring_response = subscription.to_dict()





    return monitoring_response




@app.route('/setPolicy',methods=["POST"])
def setPolicy():
    data = request.json
    print(data)
    pid=data['pol-id']
    exid=data['id']
    cells=data['cells']
    policy_db[exid]={
        "policy_id":pid,
        "cells":cells
    }
    print(policy_db)
    return data



@app.route('/VappConsume',methods=["GET","POST"])
def VappConsume():
    log_record={
        "nothing":"nothing"
    }
    if(not q.empty()):
        log_record=q.get()

    return log_record



@app.route('/netAppCallback',methods=["GET","POST"])
def netAppCallback():

    data = request.json

    d={
        'policy':policy_db,
        'msg':data
    }

    print(data)


    ex_id=data['externalId']
    if ex_id in policy_db:
        if data['locationInfo']['cellId'] not in policy_db[ex_id]['cells']:
            data['type']='alert'
        else:
            data['type']='log'
    else:
        data['type']='log'        


    payload={
        "data":data
    }
    headers = {
        'Content-type': 'application/json'
    }

    try:
        auth_response = requests.post("http://{}:{}/vapp_callback".format(vapp_db['host_name'],vapp_db['port']), headers=headers,json=payload)
    except:
        pass

    if(q.empty()):
        q.put(data)
    else:
        q.get()
        q.put(data)

    return jsonify(data)

if __name__ == '__main__':   
    app.run(host='0.0.0.0',port=5000,debug=True)


