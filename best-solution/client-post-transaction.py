from urllib.request import *
import json

req = Request(url='http://127.0.0.1:6000/inv',
              data=json.dumps(
                  {
                      "index": 2,
                      "timestamp": "03/03/2020",
                      "data": {
                          "from": "igor",
                          "to": "andrus",
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
