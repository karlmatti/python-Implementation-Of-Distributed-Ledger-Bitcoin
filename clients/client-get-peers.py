import urllib.request
url = 'http://127.0.0.1:6000/getdata?id=2bbd6787eb9809355681a382238b92ec174d894fc7d4dc0d238e08ec103bc014'
# &id=3f5006f18ac7ac5f9f12dc43431c163bd11b60a9a9e414e0d91bbfd60385c2fc
#get the result code and print it
conn = urllib.request.urlopen(url)
print("result code: " + str(conn.getcode()))

# read the data from the URL and print it
data = conn.read()
print(data)
