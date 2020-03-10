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
        return '{"index": ' + str(self.index) + ',' + \
               '"previous hash": "' + self.previous_hash + '",' + \
               '"timestamp": "' + self.timestamp + '",' + \
               '"data": ' + json.dumps(self.data, separators=(',', ':')) + ',' + \
               '"hash": "' + self.hash + \
               '"}'


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "01/01/2020", "Genesis block")

    def get_latest_block(self):
        return self.chain[len(self.chain) - 1]

    def add_block(self, new_block):
        # new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def to_string(self):
        returned_string = '{"chain":['

        for block in self.chain:
            returned_string += block.to_string() + ","
        returned_string = returned_string[:-1] + ']}'
        return returned_string

    def to_json(self):
        return json.dumps(self.to_string(), separators=(',', ':'))


class Transaction:
    def __init__(self, index, timestamp, data):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        unhashed_string = str(self.index) + \
                          self.timestamp + json.dumps(self.data, separators=(',', ':'))
        return hashlib.sha256(unhashed_string.encode('utf-8')).hexdigest()

    def to_string(self):
        return '{"index": ' + str(self.index) + ',' + \
               '"timestamp": "' + self.timestamp + '",' + \
               '"data": ' + json.dumps(self.data, separators=(',', ':')) + ',' + \
               '"hash": "' + self.hash + \
               '"}'


class Transactions:
    def __init__(self, list):
        self.list = list

    def add_transaction(self, transaction):
        self.list.append(transaction)

    def is_transaction_in_list(self, new_transaction):
        for transaction in self.list:
            if transaction == new_transaction:
                return True
        return False

    def to_string(self):
        returned_string = '{"transactions":['
        if self.list:
            for transaction in self.list:
                returned_string += transaction.to_string() + ","
            returned_string = returned_string[:-1] + ']}'
            return returned_string
        else:
            return '{"transactions":[]}'



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def handle(self):

        # print("%s:%s sent:" % (self.client_address[0], self.client_address[1]))

        chain_string = self.request.recv(1024).strip()
        data_list = chain_string.decode().split('\n')

        request_method = data_list[0].split(' ')[0]
        request_path = data_list[0].split(' ')[1]

        if request_method == 'GET':

            if '/getblocks' in request_path:
                request_path_list = request_path.split("?")
                request_path_list.pop(0)
                if '&' not in request_path_list[0]:  # /getblocks?port=6000
                    with open('blocks-' + sys.argv[1] + '.json', 'r') as f:
                        chain_string = json.load(f)
                        chain_json = json.dumps(chain_string)
                        json_length = len(chain_json)
                        headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length

                        response = headers + chain_json
                        self.request.sendall(response.encode())
                else:  # /getblocks?port=6000&id=1b7382f10c8c0cb95327f96db02155e197659c9cd1c0c55b68d5264ae0292375
                    request_path_list = request_path_list[0].split('&')
                    request_parameters = {}
                    for parameter in request_path_list:
                        key, value = parameter.split('=')
                        request_parameters[key] = value

                    with open('blocks-' + sys.argv[1] + '.json', 'r') as f:
                        chain_json = json.load(f)
                        is_id_found = False
                        returned_blocks = []

                        for block in chain_json['chain']:
                            if block['hash'] == request_parameters['id']:
                                is_id_found = True
                                returned_blocks.append(block)
                            elif is_id_found:
                                returned_blocks.append(block)

                        chain_returned_blocks = Blockchain()
                        chain_returned_blocks.chain = returned_blocks
                        chain_returned_blocks = chain_returned_blocks.to_string()

                        json_length = len(chain_returned_blocks)
                        headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                        response = headers + chain_returned_blocks
                        self.request.sendall(response.encode())

            elif '/getdata' in request_path:  # /getdata?port=6000&id=1b7382f10c8c0cb95327f96db02155e197659c9cd1c0c55b68d5264ae0292375
                request_path_list = request_path.split("?")
                request_path_list.pop(0)
                request_path_list = request_path_list[0].split('&')
                request_parameters = {}
                for parameter in request_path_list:
                    key, value = parameter.split('=')
                    request_parameters[key] = value

                with open('blocks-' + sys.argv[1] + '.json', 'r') as f:
                    chain_json = json.load(f)
                    returned_block = ""

                    for block in chain_json['chain']:
                        if block['hash'] == request_parameters['id']:
                            returned_block = json.dumps(block)

                    json_length = len(returned_block)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + returned_block
                    self.request.sendall(response.encode())

            elif '/getpeers' in request_path:
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
                    chain_string = json.load(f)
                    chain_json = json.dumps(chain_string)
                    json_length = len(chain_json)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + chain_json
                    self.request.sendall(response.encode())
        elif request_method == 'POST':
            # TODO: Tuleb realiseerida transaktsioonide laialisaatmine
            #  (a la Jaan kannab 2018-02-15 Antsule 0.0001 bitcoini)
            #  request_path = /inv, kus vastuseks on 1 või
            #  veateade: (näiteks {"errcode": ..., "errmsg": ...})

            if '/block' in request_path: # /block
                received_block = json.loads(data_list[-1])

                with open('blocks-' + sys.argv[1] + '.json', 'r') as f:
                    current_blocks = json.load(f)
                blockchain = Blockchain()
                for current_block in current_blocks['chain']:
                    block = Block(current_block['index'], current_block['timestamp'],
                                  current_block['data'], current_block['previous hash'])
                    blockchain.add_block(block)

                latest_block = blockchain.get_latest_block()

                if latest_block.hash == received_block['previous hash']:

                    new_block = Block(received_block['index'], received_block['timestamp'],
                                      received_block['data'], received_block['previous hash'])

                    blockchain.add_block(new_block)
                    blockchain.to_string()

                    blocks = open('blocks-' + sys.argv[1] + '.json', "w+")
                    blocks.write(blockchain.to_string())
                    blocks.close()

                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: plain/text\r\n\r\n' % 1
                    response = headers + "1"
                    self.request.sendall(response.encode())
                    # TODO hakka neid edasi saatma (client_blocks())

                else:
                    error_message = json.dumps({"errcode": 400, "errmsg": "Block already exists"})
                    json_length = len(error_message)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + error_message
                    self.request.sendall(response.encode())
            if '/inv' in request_path:
                received_transaction = json.loads(data_list[-1])
                with open('transactions-' + sys.argv[1] + '.json', 'r') as f:
                    current_transactions = json.load(f)
                transactions = Transactions(current_transactions['transactions'])
                if not transactions.is_transaction_in_list(received_transaction):
                    transactions.add_transaction(received_transaction)
                    # TODO lisa transactions faili
                    # TODO saada teistele transactioneid edasi client_blocks(received_transaction)
                else:
                    # TODO tagasta errmsg transaction olemas
                    pass



class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


"""
def client_blocks(ip, port):
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
"""


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

    # print(str(taltechCoin.get_latest_block().to_string()))
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

    blocks_chain = taltechCoin.to_string()

    blocks = open('blocks-' + sys.argv[1] + '.json', "w+")
    blocks.write(blocks_chain)
    blocks.close()

    my_transactions = Transactions([])

    transactions = open('transactions-' + sys.argv[1] + '.json', "w+")
    transactions.write(my_transactions.to_string())
    transactions.close()
    prev = time()
    while True:
        now = time()
        if now - prev > 60:
            with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                json_data = json.load(f)
                for peer in json_data['peers']:
                    ip, port = peer.split(':')
                    client_peers(ip, int(port))

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
