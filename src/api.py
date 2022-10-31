import time
from flask import Flask, request, jsonify
import requests
import evolved5g
import os
from queue import Queue

from evolved5g.sdk import LocationSubscriber
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


netapp_host=os.environ['netapp_host']
netapp_ip=os.environ['netapp_ip']
netapp_port=os.environ['netapp_port']

nef_url=os.environ['nef_url']
nef_user=os.environ['nef_user']
nef_pass=os.environ['nef_pass']



def get_token(username,password):
    configuration = Configuration()
    configuration.host = nef_url
    api_client = ApiClient(configuration=configuration)
    api_client.select_header_content_type(["application/x-www-form-urlencoded"])
    api = LoginApi(api_client)
    token = api.login_access_token_api_v1_login_access_token_post("", username, password, "", "", "")
    return token


def get_api_client(token):
    configuration = Configuration()
    configuration.host = nef_url
    configuration.access_token = token.access_token
    api_client = swagger_client.ApiClient(configuration=configuration)
    return api_client


token=get_token(nef_user,nef_pass)
token=token.access_token

         

app = Flask(__name__)



@app.route('/', methods=["GET", "POST"])
def index():
    # print(netapp_host)
    return netapp_host,netapp_ip


@app.route('/vapp_connect',methods=["POST"])
def vappConnect():
    data=request.json
    vapp_ip=data['vapp_ip']
    port=data['port']

    token=get_token(nef_user,nef_pass)


    vapp_db['host_name']=vapp_ip
    vapp_db['port']=port
    vapp_db['token']=token.access_token

    return vapp_db['token']


@app.route('/subscription', methods=["POST"])
def vappRegister():
    data = request.json
    _id=data['id']
    numOfreports=data['num_of_reports']
    exp_time=data['exp_time']

    token = vapp_db['token']

    location_subscriber = LocationSubscriber(nef_url, token)


    subscription=""
    resp="OK"
    try:


        subscription = location_subscriber.create_subscription(
            netapp_id=netapp_host,
            external_id=_id,
            notification_destination="http://{}:{}/netAppCallback".format(netapp_host,netapp_port),
            maximum_number_of_reports=numOfreports,
            monitor_expire_time=exp_time
        )

    except evolved5g.swagger_client.rest.ApiException as e:
        resp="ApiException"
        # print(e.message)


    return resp


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




@app.route('/get_subscriptions',methods=["GET"])
def get_subsciptions():

    resp="OK"
    location_subscriber = LocationSubscriber(nef_url, token)
    try:
        all_subscriptions = location_subscriber.get_all_subscriptions(netapp_host, 0, 100)
        print(all_subscriptions)

    except ApiException as ex:
        resp="ApiException"


    return resp


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

    # print(data)


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
    app.run(host=netapp_ip,port=netapp_port,debug=True)


