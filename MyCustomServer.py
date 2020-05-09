import threading
from time import time

import json
import socketserver
import sys
import threading
from datetime import datetime
from time import time

from ecdsa import SigningKey

from Block import Block
from Blockchain import Blockchain
from Signed_Transaction import SignedTransaction
from ThreadedTCPServer import ThreadedTCPServer
from Transaction import Transaction
from TransactionV2 import TransactionV2
from Transactions import Transactions
from client import client_packet
from client import client_peers


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def handle(self):

        # print("%s:%s sent:" % (self.client_address[0], self.client_address[1]))

        global host
        chain_string = self.request.recv(1024).strip()
        data_list = chain_string.decode().split('\n')

        request_method = data_list[0].split(' ')[0]
        request_path = data_list[0].split(' ')[1]
        # print("Request path %s" % data_list)
        if request_method == 'GET':

            if '/getblocks' in request_path:

                if "?" in request_path:  # /getblocks?id=1b7382f10c8c0cb95327f96db02155e197659c9cd1c0c55b68d5264ae0292375

                    request_parameters = {}
                    key, value = request_path.split('=')
                    key = key.split("?")[1]
                    # print("key", key)
                    # print("value", value)
                    request_parameters[key] = value

                    with open('blocks-' + sys.argv[1] + '.json', 'r') as f:
                        chain_json = json.load(f)
                        is_id_found = False
                        returned_blocks = []

                        for block in chain_json['chain']:
                            if block['hash'] == request_parameters['id']:
                                is_id_found = True

                                returned_blocks.append(Block(block['index'],
                                                             block['timestamp'],
                                                             block['data'],
                                                             block['previous hash']
                                                             ))
                            elif is_id_found:
                                returned_blocks.append(Block(block['index'],
                                                             block['timestamp'],
                                                             block['data'],
                                                             block['previous hash']))

                        chain_returned_blocks = Blockchain()
                        chain_returned_blocks.chain = returned_blocks
                        returned_blocks_string = chain_returned_blocks.to_string()

                        json_length = len(returned_blocks_string)
                        headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                        response = headers + returned_blocks_string
                        self.request.sendall(response.encode())

                else:  # /getblocks
                    with open('blocks-' + sys.argv[1] + '.json', 'r') as f:
                        chain_string = json.load(f)
                        chain_json = json.dumps(chain_string)
                        json_length = len(chain_json)
                        headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length

                        response = headers + chain_json
                        self.request.sendall(response.encode())

                    pass
                request_path_list = request_path.split("?")
                request_path_list.pop(0)

            elif '/getdata' in request_path:  # /getdata?id=1b7382f10c8c0cb95327f96db02155e197659c9cd1c0c55b68d5264ae0292375
                parameter = request_path.split("?")
                parameter.pop(0)

                request_parameters = {}

                key, value = parameter[0].split('=')
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
                for row in data_list:
                    if "Host" in row:
                        request_address = row.replace("\r", "")
                        request_address = request_address.split(" ")[1]

                        with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                            peers = json.load(f)
                        # print(request_address)
                        # print('request_address')
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

            response_list = chain_string.decode().split('\r\n\r\n')

            headers, body = response_list[0], response_list[1]
            headers = headers.split('\r\n')

            request_path = headers[0].split(' ')[1]

            if '/block' in request_path:  # /block
                received_block = json.loads(body)

                with open('blocks-' + sys.argv[1] + '.json', 'r') as f:
                    current_blocks = json.load(f)

                blockchain = Blockchain()

                for current_block in current_blocks['chain'][1:]:
                    block = Block(current_block['index'], current_block['timestamp'],
                                  current_block['data'], current_block['previous hash'])

                    blockchain.add_block(block)

                new_block = Block(received_block['index'], received_block['timestamp'],
                                  received_block['data'], received_block['previous hash'])
                if blockchain.add_block(new_block):
                    print("New block added !!!!!!!!!!!!!!!!!!!!!!!!!")

                    blocks = open('blocks-' + sys.argv[1] + '.json', "w+")
                    blocks.write(blockchain.to_string())
                    blocks.close()

                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: plain/text\r\n\r\n' % 1
                    response = headers + "1"
                    self.request.sendall(response.encode())
                    #  hakka neid edasi saatma
                    with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                        json_data = json.load(f)
                        for peer in json_data['peers']:
                            ip, port = peer.split(':')
                            client_packet(ip, int(port), 'block', new_block)

                else:
                    print("New block refused !!!!!!!!!!!!!!!!!!!!!!!!!")
                    # print(blockchain.to_string())
                    # print("/-----------------------------------/")
                    # print(new_block.to_string())
                    error_message = json.dumps({"errcode": 400, "errmsg": "Block already exists"})
                    json_length = len(error_message)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + error_message
                    self.request.sendall(response.encode())

            elif '/inv' in request_path:

                received_transaction = json.loads(body)

                received_transaction = Transaction(received_transaction['index'],
                                                   received_transaction['timestamp'],
                                                   received_transaction['data'])
                with open('transactions-' + sys.argv[1] + '.json', 'r') as f:
                    current_transactions = json.load(f)
                transactions = Transactions([])

                if current_transactions['transactions']:
                    for current_transaction in current_transactions['transactions']:
                        transaction = Transaction(current_transaction['index'],
                                                  current_transaction['timestamp'],
                                                  current_transaction['data'])
                        transactions.add_transaction(transaction)

                if transactions.is_transaction_in_list(received_transaction):
                    error_message = json.dumps({"errcode": 400, "errmsg": "Transaction already exists"})
                    json_length = len(error_message)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + error_message
                    self.request.sendall(response.encode())
                else:
                    print("Received transaction:", received_transaction.to_string())
                    transactions.add_transaction(received_transaction)

                    transactions_file = open('transactions-' + sys.argv[1] + '.json', "w+")
                    transactions_file.write(transactions.to_string())
                    transactions_file.close()

                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: plain/text\r\n\r\n' % 1
                    response = headers + "1"
                    self.request.sendall(response.encode())
                    # saada teistele transactioneid edasi client_blocks(received_transaction)
                    with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                        json_data = json.load(f)
                        for peer in json_data['peers']:
                            ip, port = peer.split(':')
                            client_packet(ip, int(port), 'transaction', received_transaction,
                                          "127.0.0.1:" + sys.argv[1])

            elif '/money' in request_path:
                """
                {
                "to": "abcde4dc843191ef4ee90e948cb9767dcf2c8da6f800a64a6f10aeaf4e1c05085a4a70cd260b9197207334963a9d8c8e",
                "sum": 4
                }
                """
                global balance
                transaction_json = json.loads(body)

                if transaction_json["sum"] <= balance:
                    balance -= transaction_json["sum"]
                    transaction_object = TransactionV2(public_key.to_string().hex(),
                                                       transaction_json["to"],
                                                       transaction_json["sum"],
                                                       datetime.now().isoformat())
                    signed_transaction_object = SignedTransaction(private_key.sign(bytes(transaction_object.to_string(),
                                                                                         'ascii')).hex(),
                                                                  transaction_object)

                    #transaction_message = signed_transaction_object.to_string()

                    response_message = json.dumps({"message": "Thanks! %s bitcoins are on the way." % transaction_json["sum"]})
                    json_length = len(response_message)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + response_message
                    self.request.sendall(response.encode())
                else:
                    error_message = json.dumps({"message": "Sorry! Not enough funds."})
                    json_length = len(error_message)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + error_message
                    self.request.sendall(response.encode())



if __name__ == "__main__":
    private_key = SigningKey.generate()
    public_key = private_key.verifying_key
    balance = 10
    host_ip = "localhost"

    host_port = int(sys.argv[1])

    server = ThreadedTCPServer((host_ip, host_port), ThreadedTCPRequestHandler)
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

    block = Block("1", "01/02/2020", 1, taltechCoin.get_latest_block().hash)

    taltechCoin.add_block(block)

    blocks_chain = taltechCoin.to_string()
    #  print(taltechCoin.get_latest_block().hash)
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
        if now - prev > 15:
            with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                json_data = json.load(f)
                # print("json_data")
                # print(json_data)
                for peer in json_data['peers']:
                    ip, port = peer.split(':')
                    # print("I have a fellow %s:%s" % (ip, port))
                    client_peers(ip, int(port), "127.0.0.1:" + sys.argv[1])

            prev = now
        else:
            pass
            # runs
