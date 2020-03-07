import json
import socket
import socketserver
import sys
import threading
from time import time
import hashlib


class Block:
    def __init__(self, index, timestamp, data, previous_hash=""):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        unhashed_string = str(self.index) + self.previous_hash + \
                          self.timestamp + json.dumps(self.data, separators=(',', ':'))
        return hashlib.sha256(unhashed_string.encode('utf-8')).hexdigest()
    def to_string(self):
        return '{"Index": '+str(self.index) +','+\
                '"Previous Hash": "'+ self.previous_hash +'",'+\
                '"Timestamp": "' + self.timestamp +'",'+\
                '"Data": ' + json.dumps(self.data, separators=(',', ':')) +','+\
                '"Hash": "' +self.previous_hash+\
                '"}'
    def to_json(self):
        return json.dumps(self.to_string(), separators=(',', ':'))


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "01/01/2020", "Genesis block", "0")

    def get_latest_block(self):
        return self.chain[len(self.chain) - 1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def handle(self):

        # print("%s:%s sent:" % (self.client_address[0], self.client_address[1]))

        json_data = self.request.recv(1024).strip()
        data_list = json_data.decode().split('\n')

        request_method = data_list[0].split(' ')[0]
        request_path = data_list[0].split(' ')[1]

        if request_method == 'GET':
            # TODO: Kui tehakse GET päring /getblocks,
            #  siis tagastada kõik blokid
            if '/getblocks' in request_path:
                request_path

            # TODO: Kui tehakse GET päring /getblocks/X,
            #  siis tagastada blokid alates X(mis on id hash) blokist

            # TODO: Kui tehakse GET päring /getdata/Y,
            #  siis tagastada konkreetne blokk Y(mis on id hash)

            if '/getpeers' in request_path:
                request_path_list = request_path.split("?")
                request_path_list.pop(0)
                if '&' not in request_path_list[0]:
                    request_port = request_path_list[0].split('=')[1]
                    request_host = data_list[1].split(':')[1].strip()
                    request_address = request_host + ':' + request_port
                    with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                        peers = json.load(f)
                    if request_address not in peers['peers']:
                        peers['peers'].append(request_address)
                        with open('peers-' + sys.argv[1] + '.json', 'w+') as f:
                            json.dump(peers, f)

                with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                    json_data = json.load(f)
                    app_json = json.dumps(json_data)
                    len_json = len(app_json)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % len_json
                    response = headers + app_json
                    self.request.sendall(response.encode())
        elif request_method == 'POST':
            # TODO: Tuleb realiseerida transaktsioonide laialisaatmine
            #  (a la Jaan kannab 2018-02-15 Antsule 0.0001 bitcoini)
            #  request_path = /inv, kus vastuseks on 1 või
            #  veateade: (näiteks {"errcode": ..., "errmsg": ...})

            # TODO: Uusi blokke saame vastu request_path = /block pealt,
            #  kus salvestame selle bloki endale (kontrollides bloki id)
            #  ja saadame edasi. Kui blokk on olemas, siis edasi ei saada.
            #  vastuseks on 1 või veateade: (näiteks {"errcode": ..., "errmsg": ...})
            pass


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def client_blocks(ip,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("/getblocks request to " + ip + str(port))
        sock.connect((ip, port))

        request = "GET /getblocks?port=%s HTTP/1.1\r\nHost: %s\r\nUser-agent: threaded-server\r\n" % (str(PORT), ip)
        sock.send(request.encode())
        print(request)
        # receive some data

        response = sock.recv(4096)
        # if len(response) < 1:

        http_response = repr(response)
        # display the response
        # print("[RECV] - length: %d" % http_response_len)

        response_body = json.loads(http_response.split("\\r\\n")[-1][0:-1])
        blocks = response_body['blocks']

        with open('blocks-' + sys.argv[1] + '.json', 'r+') as f:  # loeme peers-PORT.json failist serverid sisse
            response_body = json.load(f)
        blocks = set(blocks + response_body['blocks'])
        response_body['blocks'] = list(blocks)

        print("blocks:", list(blocks))

        with open('blocks-' + sys.argv[1] + '.json', 'w+') as f:  # kirjutame peers-PORT.json faili uuendatud andmed
            json.dump(response_body, f)

    except socket.error as e:
        pass
    finally:
        sock.close()

def client_peers(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("/getpeers request to " + ip + str(port))
        sock.connect((ip, port))

        request = "GET /getpeers?port=%s HTTP/1.1\r\nHost: %s\r\nUser-agent: threaded-server\r\n" % (str(PORT), ip)
        sock.send(request.encode())
        print(request)
        # receive some data

        response = sock.recv(4096)
        # if len(response) < 1:

        http_response = repr(response)
        http_response_len = len(http_response)
        # display the response
        # print("[RECV] - length: %d" % http_response_len)

        response_body = json.loads(http_response.split("\\r\\n")[-1][0:-1])
        peers = response_body['peers']

        with open('peers-' + sys.argv[1] + '.json', 'r+') as f:  # loeme peers-PORT.json failist serverid sisse
            response_body = json.load(f)
        peers = set(peers + response_body['peers'])
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
    # print("Server loop running in thread:", server_thread.name)


    #print(str(taltechCoin.get_latest_block().to_string()))
    # Reads default peers from peers-default.json file
    with open('peers-default.json', 'r') as f:
        data = json.load(f)

    # Creates or overwrites peers-<PORT>.json file with default peers
    f = open('peers-' + sys.argv[1] + '.json', "w+")
    f.write(json.dumps(data))
    f.close()
    # Creating data for block
    taltechCoin = Blockchain()
    block = Block("1", "01/02/2020",
                  {"from": "mult",
                   "to": "sulle",
                   "amount": 2000000})
    taltechCoin.add_block(block)
    blocks_chain = '{"chain": [' + block.to_string() + ']}'
    blocks = open('blocks-' + sys.argv[1] + '.json', "w+")

    blocks.write(blocks_chain)
    blocks.close()


    prev = time()
    while True:
        now = time()
        if now - prev > 10:
            with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                json_data = json.load(f)
                for peer in json_data['peers']:
                    ip, port = peer.split(':')
                    client_peers(ip, int(port))
            with open('blocks-' + sys.argv[1] + '.json', 'r') as blocks:
                json_data = json.load(blocks)
                for block in json_data['chain']:
                    # TODO: do send all blocks method
                    # TODO: do send blocks method since X block
                    # TODO: do send transaction data
                    client_blocks(ip, int(port))
            # print("10 sec")
            prev = now
        else:
            pass
            # runs




            # taltechCoin = Blockchain()
            # block = Block('1', "01/02/2020",
            #               {"from": "mult",
            #                "to": "sulle",
            #                "amount": 2000000})
            # taltechCoin.add_block(block)
            # print(str(taltechCoin.get_latest_block().to_string()))