import time
from flask import Flask, request, jsonify
import threading
from queue import Queue
import socket
import requests


send_lock = threading.Lock()


stoken="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NDYxNDUyODYsInN1YiI6IjEifQ.3ACLbt1o_W8DdSyHpY6lwOlLRcsXCUoQXRxDXSMCZng"
headers = {
    'Authorization': "Bearer {}".format(stoken),
    'Content-type': 'application/json'
}

policy_db={}


class CallbackThread(threading.Thread):
    def __init__(self, queue, args=(), kwargs=None):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.queue = queue
        self.daemon = True
        self.receive_messages = args[0]
        self.s = socket.socket()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setblocking(False)         
        # self.host = socket.gethostname()
        self.host = "172.18.18.136"

        self.port = 12346                

    def run(self):
        
        print(threading.currentThread().getName(), self.receive_messages)
        while True:
            val = self.queue.get()
            try:
                self.s.connect((self.host, self.port))
            except BlockingIOError:
                pass
            except ConnectionAbortedError:
                pass
            except ConnectionResetError:
                pass
            except OSError:
                pass

            self.do_thing_with_message(val)

    def do_thing_with_message(self, val):
        if self.receive_messages:
            with send_lock:
                message=val['msg']
                print("Received from NEF_emulator {}".format(message))
                ex_id=val['msg']['externalId']
                if ex_id in policy_db:
                    if val['msg']['locationInfo']['cellId'] not in policy_db[ex_id]['cells']:
                        val['msg']['type']='alert'
                    else:
                        val['msg']['type']='log'
                else:
                    val['msg']['type']='log'               
                try:
                    print(str(message))
                    self.s.send(bytes(str(message),encoding="utf-8"))
                    d=self.s.recv(1)
                    if not d: self.s.close()
                    
                except ConnectionRefusedError:
                    pass
                except BrokenPipeError:

                    pass     
                except OSError:
                    pass     
           

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    return "kati"

@app.route('/subscription', methods=["POST"])
def vappRegister():
    data = request.json
    _id=data['id']
    numOfreports=data['num_of_reports']
    exp_time=data['exp_time']


    payload={
      "externalId": _id,
      "notificationDestination": "http://mynetapp:5000/netAppCallback",
      "monitoringType": "LOCATION_REPORTING",
      "maximumNumberOfReports": numOfreports,
      "monitorExpireTime": exp_time
    }

    print(payload)


    auth_response = requests.post("http://backend/nef/api/v1/3gpp-monitoring-event/v1/netApp/subscriptions", headers=headers,json=payload)


    resp=auth_response.json()
    print(resp)

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





@app.route('/netAppCallback',methods=["GET","POST"])
def netAppCallback():
    # data = request.json
    # print(data)
    # return jsonify({"ans":"LOL"})
    data = request.json

    d={
        'policy':policy_db,
        'msg':data
    }
    callbackThread.queue.put(d)
    print("Sending data to Vapp")
    return jsonify(data)

if __name__ == '__main__':
    q = Queue()
    callbackThread = CallbackThread(q, args=(1,))
    callbackThread.start()    
    app.run(host='0.0.0.0',port=5000,debug=True)



# curl localhost:5000/netAppCallback -d "{\"foo\": \"bar\"}" -H 'Content-Type: application/json'