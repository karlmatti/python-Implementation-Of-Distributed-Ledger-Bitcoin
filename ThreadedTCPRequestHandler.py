import json
import socketserver
import sys

from Block import Block
from Blockchain import Blockchain
from Transaction import Transaction
from Transactions import Transactions
from client import client_blocks


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
        #print("Request path %s" % data_list)
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
            # print("response list", response_list)
            headers, body = response_list[0], response_list[1]
            headers = headers.split('\r\n')
            # print("headers.split()")
            # print(headers)
            # print("body")
            # print(body)
            request_path = headers[0].split(' ')[1]
            # print("request_path")
            # print(request_path)
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
                            client_blocks(ip, int(port), 'block', new_block)

                else:
                    print("New block refused !!!!!!!!!!!!!!!!!!!!!!!!!")
                    #print(blockchain.to_string())
                    #print("/-----------------------------------/")
                    #print(new_block.to_string())
                    error_message = json.dumps({"errcode": 400, "errmsg": "Block already exists"})
                    json_length = len(error_message)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + error_message
                    self.request.sendall(response.encode())

            if '/inv' in request_path:

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
                    print("Received transaction:",received_transaction.to_string())
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
                            client_blocks(ip, int(port), 'transaction', received_transaction, "127.0.0.1:" + sys.argv[1])
