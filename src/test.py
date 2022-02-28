from evolved5g.swagger_client import LoginApi, User
import emulator_utils
import requests
import json


def test():
    """
    Demonstrate how to interact with the Emulator, to a token and the current logged in User
    """

    # token = emulator_utils.get_token()
    # api_client = emulator_utils.get_api_client(token)
    # api = LoginApi(api_client)

    # stoken="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzY5MDE3MjYsInN1YiI6IjEifQ.3f4ln6Pu4X5Lr69rfX5coTOiq0uLdJmKvtbocsKf31E"
    # headers = {
    #     'Authorization': "Bearer {}".format(stoken),
    #     'Content-type': 'application/json'
    # }


    # payload={
    #   "externalId": "10003@domain.com",
    #   "notificationDestination": "http://172.18.18.136:5000/netAppCallback",
    #   "monitoringType": "LOCATION_REPORTING",
    #   "maximumNumberOfReports": 100,
    #   "monitorExpireTime": "2021-11-10T12:41:39.781Z"
    # }
    
    payload={
        "id":"1003@domain.com",
        "num_of_reports":100,
        "exp_time":"2021-11-10T12:41:39.781Z"
    }



    auth_response = requests.post("http://localhost:8888/api/v1/3gpp-monitoring-event/v1/netApp/subscriptions", headers=headers,json=payload)


    print(auth_response.json())

if __name__ == "__main__":
    test()