from urllib.request import *
import json

req = Request(url='http://127.0.0.1:6000/block',
              data=json.dumps(
                  {
                      "index": 2,
                      "previous hash": "???",
                      "timestamp": "01/02/2020",
                      "data": 3,
                      "hash": "x"
                  }
              ).encode(),
              headers={},
              method='POST')
with urlopen(req) as res:
    body = res.read().decode()
    print(body)
