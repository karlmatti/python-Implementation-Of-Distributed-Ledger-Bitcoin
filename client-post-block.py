from urllib.request import *
import json

req = Request(url='http://127.0.0.1:6000/block',
              data=json.dumps(
                  {
                      "index": 2,
                      "previous hash": "3f5006f18ac7ac5f9f12dc43431c163bd11b60a9a9e414e0d91bbfd60385c2fc",
                      "timestamp": "01/02/2020",
                      "data": {
                          "from": "iphone",
                          "to": "android",
                          "amount": 1235
                      },
                      "hash": "x"
                  }
              ).encode(),
              headers={},
              method='POST')
with urlopen(req) as res:
    body = res.read().decode()
    print(body)
