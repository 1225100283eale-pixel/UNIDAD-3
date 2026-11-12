import json
import requests
from getpass import getpass

requests.packages.urllib3.disable_warnings()
api_url = "https://10.10.20.48/restconf/data/ietf-interfaces:interfaces/interface=Loopback99"

headers = {
    "Accept": "application/yang-data+json",
    "Content-type": "application/yang-data+json",
}

basicauth = ("developer", getpass("Contraseña del sandbox: "))  
yangConfig = {
    "ietf-interfaces:interface": {
        "name": "Loopback99",
        "description": "WHATEVER99",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
        "ietf-ip:ipv4": {
            "address": [
                {
                    "ip": "99.99.99.99",
                    "netmask": "255.255.255.0"
                }
            ]
        },
        "ietf-ip:ipv6": {}
    }
}
resp = requests.put(
    api_url,
    data=json.dumps(yangConfig),
    auth=basicauth,
    headers=headers,
    verify=False
)

if 200 <= resp.status_code <= 299:
    print("STATUS OK: {}".format(resp.status_code))
else:
    print("Error code {}, reply: {}".format(resp.status_code, resp.json()))