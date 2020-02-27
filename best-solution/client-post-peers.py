from urllib.request import *
import json

req = Request(url='http://127.0.0.1:6000/',
              data=json.dumps({'peers': ['127.0.0.1:6007', '127.0.0.1:6015']}).encode(),
              headers={},
              method='POST')
with urlopen(req) as res:
    body = res.read().decode()
    print(body)