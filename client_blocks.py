import json
import socket
import socketserver
import sys

def client_blocks(ip, port, packet_type, packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip, port))
        if packet_type == 'transaction':
            request = "POST /inv HTTP/1.1\r\nHost: %s:%s\r\nUser-agent: transaction-santa\r\n\r\n" % (ip, port)
            request += packet.to_string()
            print("transaction-santa request", request)
            sock.send(request.encode())
        elif packet_type == 'block':
            request = "POST /block HTTP/1.1\r\nHost: %s:%s\r\nUser-agent: block-santa\r\n\r\n" % (ip, port)
            request += packet.to_string()
            print("block-santa request", request)
            sock.send(request.encode())



    except socket.error as e:

        server_address = ip + ':' + str(port)
        with open('peers-' + sys.argv[1] + '.json', 'r+') as f:  # loeme peers-PORT.json failist serverid sisse
            response_body = json.load(f)

        peers = list(response_body['peers'])

        deleted_peer_index = peers.index(server_address)
        peers.pop(deleted_peer_index)  # kustutame serveri nimekirjast
        response_body['peers'] = peers

        with open('peers-' + sys.argv[1] + '.json', 'w+') as f:  # kirjutame peers-PORT.json faili uuendatud andmed
            json.dump(response_body, f)

        print("Error404 - cannot find " + server_address + ", deleted from list.")

    finally:
        sock.close()
