import socket
import sys
import json

HOST, PORT = "127.0.0.1", 8001
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
json_dict = {'param1': 'val1',
             'param2': 'val2'}

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    kamarajura = str(HOST).encode()+str(' ').encode()+str(PORT).encode()+str(' ').encode()
    json_data = json.dumps(json_dict)
    print("Sent:     {}".format(kamarajura))
    sock.sendall(kamarajura)

    # Receive data from the server and shut down
    received = sock.recv(1024)
finally:
    sock.close()


print ("Received: {}".format(received))