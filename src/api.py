import time
from flask import Flask, request, jsonify
import requests
import emulator_utils
import evolved5g
from evolved5g.sdk import LocationSubscriber
from evolved5g.swagger_client.rest import ApiException
import pymongo
from pymongo import MongoClient


policy_db={}

vapp_db={
    'host_name':"",
    'port':0,
    'token':0
}


def get_db():
    client = MongoClient(host='mynetapp_db',
                         port=27018, 
                         username='root', 
                         password='pass',
                        authSource="admin")
    db = client["policies_db"]
    return db



netapp_host="mynetapp"
token=emulator_utils.get_token()
token=token.access_token
         

app = Flask(__name__)



@app.route('/', methods=["GET", "POST"])
def index():
    policy_db={}
    return "ok"




@app.route('/policies')
def get_stored_policies():
    db = get_db()
    _policies = db.animal_tb.find()
    policies = [{"id": policy["id"], "type": animal["type"]} for policy in _policies]
    return jsonify({"policies": policies})




@app.route('/vapp_connect',methods=["POST"])
def vappConnect():
    data=request.json
    vapp_ip=data['vapp_ip']
    port=data['port']

    token=emulator_utils.get_token()


    vapp_db['host_name']=vapp_ip
    vapp_db['port']=port
    vapp_db['token']=token.access_token

    print(vapp_db)
    return vapp_db['token']


@app.route('/subscription', methods=["POST"])
def vappRegister():
    data = request.json
    _id=data['id']
    numOfreports=data['num_of_reports']
    exp_time=data['exp_time']

    netapp_id = "mynetapp"
    host = emulator_utils.get_host_of_the_nef_emulator()
    token = vapp_db['token']

    location_subscriber = LocationSubscriber(host, token)


    subscription=""
    reps="OK"
    try:


        subscription = location_subscriber.create_subscription(
            netapp_id=netapp_id,
            external_id=_id,
            notification_destination="http://{}:5000/netAppCallback".format(netapp_host),
            maximum_number_of_reports=numOfreports,
            monitor_expire_time=exp_time
        )

    except evolved5g.swagger_client.rest.ApiException as e:
        resp="ApiException"
        print(e.message)


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
    host = emulator_utils.get_host_of_the_nef_emulator()
    location_subscriber = LocationSubscriber(host, token)
    try:
        all_subscriptions = location_subscriber.get_all_subscriptions("mynetapp", 0, 100)
        print(all_subscriptions)

    except ApiException as ex:
        resp="ApiException"


    return resp



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

    print(data)

    return jsonify(data)

if __name__ == '__main__':   
    app.run(host='0.0.0.0',port=5000,debug=True)


