import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
target_host = 'localhost'
server_address = (target_host, 6000)
client_socket.connect(server_address)

request_header = "GET /getpeers HTTP/1.1\r\nHost:%s\r\nUser-agent: client_4\r\n" % target_host
client_socket.send(request_header.encode())

response = ''
while True:
    recv = client_socket.recv(1024)
    if not recv:
        break
    #response += recv

print(response)
print(recv)
client_socket.close()