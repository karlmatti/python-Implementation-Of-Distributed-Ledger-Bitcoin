import urllib.request
url = 'http://127.0.0.1:6000/getblocks?port=6001&id=1b7382f10c8c0cb95327f96db02155e197659c9cd1c0c55b68d5264ae0292375'

#get the result code and print it
conn = urllib.request.urlopen(url)
print("result code: " + str(conn.getcode()))

# read the data from the URL and print it
data = conn.read()
print(data)
