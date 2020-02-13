import socket
target_host = "localhost"

target_port = 6000  # create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
client.connect((target_host, target_port))

# send some data
request = "GET /getpeers HTTP/1.1\r\nHost:%s\r\nUser-agent: client_4\r\n" % target_host
client.send(request.encode())
print(request)
# receive some data
response = client.recv(4096)
http_response = repr(response)
http_response_len = len(http_response)

# display the response
print("[RECV] - length: %d" % http_response_len)
print(http_response)