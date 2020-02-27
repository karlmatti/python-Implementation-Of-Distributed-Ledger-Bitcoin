import json
import socket
import socketserver
import sys
import threading
from time import time


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def handle(self):

        print("%s:%s sent:" % (self.client_address[0], self.client_address[1]))

        json_data = self.request.recv(1024).strip()
        data_list = json_data.decode().split('\n')
        request_method = data_list[0].split(' ')[0]
        request_path = data_list[0].split(' ')[1]

        if request_method == 'GET':

            if request_path == '/getpeers':
                with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                    json_data = json.load(f)
                    app_json = json.dumps(json_data)
                    len_json = len(app_json)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % len_json
                    response = headers + app_json
                    self.request.sendall(response.encode())


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:

        sock.connect((ip, port))
        request = "GET /getpeers HTTP/1.1\r\nHost:%s\r\nUser-agent: client_4\r\n" % ip
        sock.send(request.encode())
        print(request)
        # receive some data

        response = sock.recv(4096)
        #if len(response) < 1:

        http_response = repr(response)
        http_response_len = len(http_response)
        # display the response
        print("[RECV] - length: %d" % http_response_len)
        print(http_response)
        # TODO: vaata mis peerid on olemas ja lisa puudu olevad

    except socket.error as e:
        print("Hallo hallo, läksin perse")
        # TODO: kustuta peer ära, sest vastus on 404
        with open('peers-' + sys.argv[1] + '.json', 'r+') as f:

            response_body = json.load(f)
            print(response_body['peers'])

            server_address = str(ip) + ':' + str(port)
            print('server_address on ' + server_address)
            if server_address in response_body['peers']:

                deleted_peer_index = peer.index(server_address)  # See IP peab olema muutujana
                response_body['peers'].pop(deleted_peer_index)

                json_data = json.dumps(response_body)
                json.dump(json_data,f)

    finally:
        sock.close()


if __name__ == "__main__":

    HOST = "localhost"

    PORT = int(sys.argv[1])

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # start a thread with the server.
    # the thread will then start one more thread for each request.
    server_thread = threading.Thread(target=server.serve_forever)

    # exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)

    # Reads default peers from peers-default.json file
    with open('peers-default.json', 'r') as f:
        data = json.load(f)

    # Creates or overwrites peers-<PORT>.json file with default peers
    f = open('peers-' + sys.argv[1] + '.json', "w+")
    f.write(json.dumps(data))
    f.close()

    prev = time()
    while True:
        now = time()
        if now - prev > 10:
            with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                json_data = json.load(f)
                for peer in json_data['peers']:
                    ip,port = peer.split(':')
                    client(ip, int(port))
            print("10 sec")
            prev = now
        else:
            pass
            # runs

