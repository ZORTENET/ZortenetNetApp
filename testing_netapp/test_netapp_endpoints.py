from threading import Thread
import signal
import sys
from threading import Event
import requests
from time import sleep
import json
import sys


# netapp_url="https://zortenet.apps.ocp-epg.tid.es"

netapp_url="http://localhost:5001"


def signal_handler(sig, frame):
	print('You pressed Ctrl+C!')

	# resp=requests.get("{}/stop_ues".format(netapp_url),verify=False)
	# print("Started_ues",resp.json())

	event.set()
	thread.join()
	sys.exit()



resp=requests.get("{}/start_ues".format(netapp_url),verify=False)
print("Started_ues",resp.json())




payload={
    "vapp_ip":"does_not_matter",
    "port":"777"
}
headers = {
    'Content-type': 'application/json'
}

auth_response = requests.post("{}/vapp_connect".format(netapp_url), headers=headers,json=payload)

print(auth_response,"vapp_connect")


payload={
    "id":"10003@domain.com",
    "num_of_reports":"100",
    "exp_time":'2022-11-12T12:41:39.781Z'
}
headers = {
    'Content-type': 'application/json'
}

auth_response = requests.post("{}/subscription".format(netapp_url), headers=headers,json=payload)

print(auth_response,"subscription")



payload={
    "id":"10003@domain.com",
    "pol-id":"0",
    "cells":"AAAAA1001,AAAAA1002"
}
headers = {
    'Content-type': 'application/json'
}

auth_response = requests.post("{}/setPolicy".format(netapp_url), headers=headers,json=payload)

print(auth_response,"policy creation")


event = Event()


def location_updates(event):

	while True:
        
		if event.is_set():
			break
        # report a message
		resp = requests.get("{}/VappConsume".format(netapp_url))
		data=json.loads(resp.text)
		if("nothing" in data):
			continue
		else:
			d={
				'type':"",
				'msg':""
			}

			if(data['type'] == 'log'):
				log='NORMAL LOG: ue {} with ip {} is using cell {}'.format(data['externalId'],data['ipv4Addr'],data['locationInfo']['cellId'])
				d['type']='LOG'
				d['msg']=log
			else:
				alert='ALERT LOG: ue {} with ip {} is using cell {}'.format(data['externalId'],data['ipv4Addr'],data['locationInfo']['cellId'])
				d['type']='ALERT'
				d['msg']=alert

			sleep(1)
			print(d)


thread = Thread(target=location_updates, args=(event,))


thread.start()



signal.signal(signal.SIGINT, signal_handler)