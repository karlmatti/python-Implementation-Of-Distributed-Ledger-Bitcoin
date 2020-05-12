import json
import socket
import sys


def client_packet(ip, port, packet_type, packet, host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip, port))
        if packet_type == 'transaction':
            request = get_http_request_header("post", "/inv", host, "transaction-santa")
            request += packet.to_string()
            #print("transaction-santa request", request)
            sock.send(request.encode())
        elif packet_type == 'block':

            request = get_http_request_header("post", "/block", host, "block-santa")

            request += packet.to_string()
            #print("block-santa request", request)
            sock.send(request.encode())



    except socket.error as e:

        get_socket_error(ip, port)

    finally:
        sock.close()


def client_peers(ip, port, host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        #print("/getpeers request to " + ip + ':' + str(port))
        sock.connect((ip, port))

        request = get_http_request_header("get", "/getpeers",  host, "threaded-server")

        sock.send(request.encode())

        # receive some data

        response = sock.recv(4096)

        http_response = repr(response)
        #print('client_peers - http_response')
        #print(http_response)

        response_body = json.loads(http_response.split("\\r\\n")[-1][0:-1])
        peers = response_body['peers']

        with open('peers-' + sys.argv[1] + '.json', 'r+') as f:  # loeme peers-PORT.json failist serverid sisse
            response_body = json.load(f)
        peers = set(peers + response_body['peers'])
        #print('peers')
        #print(peers)
        response_body['peers'] = list(peers)

        #print("Peers:", list(peers))

        with open('peers-' + sys.argv[1] + '.json', 'w+') as f:  # kirjutame peers-PORT.json faili uuendatud andmed
            json.dump(response_body, f)

    except socket.error as e:
        get_socket_error(ip, port)
    finally:
        sock.close()


def get_http_request_header(method, path, host, user_agent):
    if method.lower() == "get":
        return "GET %s HTTP/1.1\r\nHost: %s\r\nUser-agent: %s\r\n\r\n" % (path,  host, user_agent)
    elif method.lower() == "post":
        return "POST %s HTTP/1.1\r\nHost: %s\r\nUser-agent: %s\r\n\r\n" % (path,  host, user_agent)


def get_socket_error(ip, port):
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
