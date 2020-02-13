import socket
import json

HOST, PORT = "localhost", 6000
json_dict = {'param1': 'val1',
             'param2': 'val2'}
json_data = json.dumps(json_dict)
byte_data = json_data.encode()
# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(byte_data)

    # Receive data from the server and shut down
    received = sock.recv(1024)
finally:
    sock.close()

print ("Sent:     {}".format(byte_data.decode()))
print ("Received: {}".format(received))