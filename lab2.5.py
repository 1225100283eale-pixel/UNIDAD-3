import json
import requests
from getpass import getpass
requests.packages.urllib3.disable_warnings()
api_url = "https://10.10.20.48/restconf/data/ietf-interfaces:interfaces"

headers = {
    "Accept": "application/yang-data+json",
    "Content-type": "application/yang-data+json",
}

basicauth = ("developer", getpass("Contraseña del sandbox: "))
resp = requests.get(
    api_url,
    auth=basicauth,
    headers=headers,
    verify=False
)
response_json = resp.json()
print(json.dumps(response_json, indent=4))