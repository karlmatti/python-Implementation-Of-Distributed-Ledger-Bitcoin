import urllib.request
try:
    url = 'http://127.0.0.1:6000/'

    # now, with the below headers, we defined ourselves as a simpleton who is
    # still using internet explorer.
    headers = {}
    headers['User-Agent'] = "client_urllib_get"
    headers['Host'] = 'http://127.0.0.1:6000/'
    req = urllib.request.Request(url, headers = headers)
    resp = urllib.request.urlopen(req)
    respData = resp.read()
    print('response:' + str(respData))
    saveFile = open('withHeaders.txt','w')
    saveFile.write(str(respData))
    saveFile.close()
except Exception as e:
    print(str(e))