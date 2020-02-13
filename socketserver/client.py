import urllib.request
import urllib.parse
import http
import json


url = 'http://127.0.0.1:6000/'
json_dict = {'param1': 'val1',
             'param2': 'value'}

# convert json_dict to JSON
json_data = json.dumps(json_dict)
# lambi_data = "koNn hYpPaS"
byte_data = json_data.encode()

req = urllib.request.Request(url, byte_data)
# req.add_header('Content-Type', 'text/html')
req.add_header('Content-Type', 'application/json')
try:
    response = urllib.request.urlopen(req)

    the_page = response.read()

except http.client.HTTPException as e:
    print(e)
"""
# convert json_dict to JSON
json_data = json.dumps(json_dict)
# lambi_data = "koNn hYpPaS"
byte_data = json_data.encode()

req = urllib.request.Request(url, byte_data)
# req.add_header('Content-Type', 'text/html')
req.add_header('Content-Type', 'application/json')
try:
    response = urllib.request.urlopen(req)

    the_page = response.read()

except http.client.HTTPException as e:
    print(e)
"""