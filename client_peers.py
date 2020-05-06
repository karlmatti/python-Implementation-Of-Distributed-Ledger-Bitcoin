import json
import socket
import sys

def client_peers(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print("/getpeers request to " + ip + ':' + str(port))
        sock.connect((ip, port))

        request = "GET /getpeers HTTP/1.1\r\nHost: %s:%s\r\nUser-agent: threaded-server\r\n" % (ip, str(port))

        sock.send(request.encode())

        # receive some data

        response = sock.recv(4096)

        http_response = repr(response)
        print('http_response')
        print(http_response)

        response_body = json.loads(http_response.split("\\r\\n")[-1][0:-1])
        peers = response_body['peers']

        with open('peers-' + sys.argv[1] + '.json', 'r+') as f:  # loeme peers-PORT.json failist serverid sisse
            response_body = json.load(f)
        peers = set(peers + response_body['peers'])
        print('peers')
        print(peers)
        response_body['peers'] = list(peers)

        print("Peers:", list(peers))

        with open('peers-' + sys.argv[1] + '.json', 'w+') as f:  # kirjutame peers-PORT.json faili uuendatud andmed
            json.dump(response_body, f)

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
