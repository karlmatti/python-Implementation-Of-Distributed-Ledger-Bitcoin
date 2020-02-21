import urllib.request
url = 'http://127.0.0.1:6001/getpeers'
#get the result code and print it
conn = urllib.request.urlopen(url)
print("result code: " + str(conn.getcode()))

# read the data from the URL and print it
data = conn.read()
print(data)
# TODO: uuenda klienti, info allpool
# Mina olen localhost:6000
# teen tsükliliselt /getpeers päringuid serverite vastu, mille saan peers-6000.txt failist
    # loen localhost:6000 serverite nimekirja
    # võrdlen localhost:6001 serverite nimekirjaga
    # kui servereid on 6001'st puudu, siis lisan puudu olevad IP'd post päringuga 6001 serverisse




"""
import urllib.error
url = 'http://127.0.0.1:6001/'
try:
    conn = urllib.request.urlopen(url)
except urllib.error.HTTPError as e:
    # Return code error (e.g. 404, 501, ...)
    # ...
    print('HTTPError: {}'.format(e.code))
except urllib.error.URLError as e:
    # Not an HTTP-specific error (e.g. connection refused)
    # ...
    # Kustuta peer ära
    print('URLError: {}'.format(e.reason))
else:
    # 200
    # ...
    print('good')
"""
"""
#get the result code and print it
print("result code: " + str(webUrl.getcode()))

# read the data from the URL and print it
data = webUrl.read()
print (data)
"""