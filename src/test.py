import subprocess
import json


# capif_registration={
# 	"certs_folder":".",
# 	"capif_host":"capifcore",
# 	"capif_http_port":8080,
# 	"capif_http_port":443,
# 	"capif_netapp_uname":"zortenet_netapp_dummy",
# 	"capif_netapp_pass":"pass",
# 	"capif_callback_url":"zorte_url",
# 	"desc":"Zortnet's anomaly detection netapp",
# 	"csr_com_name":"zorte netapp",
# 	"csr_org_unit":"none1",
# 	"csr_org":"none2",
# 	"csr_locality":"Athens",
# 	"csr_state_name":"Athens",
# 	"csr_country":"Greece",
# 	"csr_email":"test@example.com"
# }


capif_registration={
  "folder_to_store_certificates": ".",
  "capif_host": "capifcore",
  "capif_http_port": 8080,
  "capif_https_port": 443,
  "capif_netapp_username": "zortenet_netapp_dummy",
  "capif_netapp_password": "pass",
  "capif_callback_url": "http://zorte_netapp:5000",
  "description": ",test_app_description",
  "csr_common_name": "test_app_common_name",
  "csr_organizational_unit": "test_app_ou",
  "csr_organization": "test_app_o",
  "crs_locality": "Athens",
  "csr_state_or_province_name": "Athens",
  "csr_country_name": "GR",
  "csr_email_address": "test@example.com"
}




json_object = json.dumps(capif_registration, indent=4)
with open("capif_registration.json", "w") as outfile:
    outfile.write(json_object)


# print(args.replace("\n"," "))
result = subprocess.run(["evolved5g", "register-and-onboard-to-capif","--config_file_full_path=capif_registration.json"], stderr=subprocess.PIPE, text=True)
print(result.stderr)
