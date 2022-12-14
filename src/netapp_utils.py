from evolved5g.sdk import LocationSubscriber ,CAPIFInvokerConnector
from evolved5g.swagger_client.rest import ApiException
from evolved5g.swagger_client import LoginApi, User ,Configuration ,ApiClient
from evolved5g.swagger_client.models import Token

def get_token(username,password,nef_url):
    configuration = Configuration()
    configuration.host = nef_url
    api_client = ApiClient(configuration=configuration)
    api_client.select_header_content_type(["application/x-www-form-urlencoded"])
    api = LoginApi(api_client)
    token = api.login_access_token_api_v1_login_access_token_post("", username, password, "", "", "")
    return token.access_token


def get_api_client(token):
    configuration = Configuration()
    configuration.host = nef_url
    configuration.access_token = token.access_token
    api_client = swagger_client.ApiClient(configuration=configuration)
    return api_client




def monitor_subscription(expire_time,netapp_id,external_id,times, host, access_token, certificate_folder, capifhost, capifport, callback_server):
    expire_time = expire_time
    netapp_id = netapp_id
    location_subscriber = LocationSubscriber(host, access_token, certificate_folder, capifhost, capifport)
    external_id = external_id

    subscription = location_subscriber.create_subscription(
        netapp_id=netapp_id,
        external_id=external_id,
        notification_destination=callback_server,
        maximum_number_of_reports=times,
        monitor_expire_time=expire_time
    )
    monitoring_response = subscription.to_dict()

    return monitoring_response