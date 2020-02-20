import urllib.request
url = 'http://127.0.0.1:6000/'
#get the result code and print it
conn = urllib.request.urlopen(url)
print("result code: " + str(conn.getcode()))

# read the data from the URL and print it
data = conn.read()
print (data)


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