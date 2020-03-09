from urllib.request import *
import json

req = Request(url='http://127.0.0.1:6000/block',
              data=json.dumps(
                  {
                      "Index": 1,
                        "Previous Hash": "0ef767065141dcb598c08c2f695c525fe474dd4c2c6b68572fd639e409195ea7",
                        "Timestamp": "01/02/2020",
                        "Data": {
                            "from": "mult",
                            "to": "sulle",
                            "amount": 2000000
                        },
                        "Hash": "1b7382f10c8c0cb95327f96db02155e197659c9cd1c0c55b68d5264ae0292375"
                   }
            ).encode(),
              headers={},
              method='POST')
with urlopen(req) as res:
    body = res.read().decode()
    print(body)