import threading
from time import time

import json
import socketserver
import sys
import threading
from datetime import datetime
from time import time
import string
import random

from ecdsa import SigningKey, VerifyingKey, BadSignatureError
from BlockV2 import BlockV2
from BlockchainV2 import Blockchain
from SignedTransaction import SignedTransaction
from ThreadedTCPServer import ThreadedTCPServer
from TransactionV2 import TransactionV2
from SignedTransactionChain import SignedTransactionChain
from client import client_packet
from client import client_peers

def oneBitcoinTransactionToMyWallet():
    transactionToMyself = TransactionV2("System", public_key.to_string().hex(),
                                 1, datetime.now().isoformat())
    signedTransactionToMyself = SignedTransaction("System", transactionToMyself)
    return signedTransactionToMyself

def startCreatingBlock(index, signedTransactionChain, my_public_key, previous_hash):
    stringLength = 20
    lettersAndDigits = string.ascii_letters + string.digits

    new_block = BlockV2(index, datetime.now().isoformat(), "nonce", my_public_key.to_string().hex(),
                          signedTransactionChain, previous_hash)
    while new_block.hash[0:4] != "0000":
        new_block.nonce = (''.join(random.choice(lettersAndDigits) for _ in range(stringLength)))
        new_block.hash = new_block.calculate_hash()

    return new_block


def readBlockChainFromFile():
    with open('blocks-' + sys.argv[1] + '.json', 'r') as f:
        blocks_json = json.load(f)

        blockChain = Blockchain()
        for block_levels in blocks_json['chain']:

            for block in block_levels:

                signedTransactionChain = SignedTransactionChain([])

                for signedTransactionDict in block["transactions"]:
                    transactionDict = signedTransactionDict["transaction"]
                    print('signedTransactionDict["transaction"]', type(signedTransactionDict["transaction"]))
                    signedTransaction = SignedTransaction(
                        signedTransactionDict["signature"],
                        TransactionV2(transactionDict["from"], transactionDict["to"],
                                      transactionDict["sum"], transactionDict["timestamp"]))
                    signedTransactionChain.add_transaction(signedTransaction)
                blockChain.add_block(BlockV2(block["nr"], block["previous_hash"],block["timestamp"],
                                             block["creator"], signedTransactionChain, block["nonce"]))
    return blockChain


def writeBlockChainToFile(currentBlockChain):
    blocks = open('blocks-' + sys.argv[1] + '.json', "w+")
    blocks.write(currentBlockChain.to_string())
    blocks.close()



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
                    error_message = json.dumps({"errcode": 400, "errmsg": "Block already exists"})
                    json_length = len(error_message)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + error_message
                    self.request.sendall(response.encode())

            elif '/inv' in request_path:

                received_transaction = json.loads(body)
                transactionV2 = TransactionV2(received_transaction['transaction']['from'],
                                              received_transaction['transaction']['to'],
                                              received_transaction['transaction']['sum'],
                                              received_transaction['transaction']['timestamp'])
                signature = received_transaction['signature']
                signed_transaction = SignedTransaction(signature, transactionV2)

                with open('transactions-' + sys.argv[1] + '.json', 'r') as f:
                    current_transactions = json.load(f)
                signedTransactionChain = SignedTransactionChain([])

                if current_transactions['transactions']:
                    for current_transaction in current_transactions['transactions']:
                        transaction = SignedTransaction(current_transaction['signature'],
                                                        TransactionV2(current_transaction['transaction']['from'],
                                                                      current_transaction['transaction']['to'],
                                                                      current_transaction['transaction']['sum'],
                                                                      current_transaction['transaction']['timestamp']))

                        signedTransactionChain.add_transaction(transaction)

                if signedTransactionChain.is_transaction_in_list(signed_transaction):
                    error_message = json.dumps({"errcode": 400, "errmsg": "Transaction already exists"})
                    json_length = len(error_message)
                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                    response = headers + error_message
                    self.request.sendall(response.encode())
                else:

                    new_signature = bytearray.fromhex(signed_transaction.signature)
                    new_message = bytes(signed_transaction.transaction.to_string(), 'ascii')
                    new_public_key = VerifyingKey.from_string(
                        bytearray.fromhex(signed_transaction.transaction.trn_from))
                    try:
                        if new_public_key.verify(new_signature, new_message):  # verifitseeri saadud transaktsioon
                            blockChain = readBlockChainFromFile()
                            blockChain.has_enough_funds(public_key.to_string().hex(), signed_transaction.transaction.trn_sum)
                            # TODO: fixi kas transaktsiooni tegijal on piisavalt raha

                            signedTransactionChain.add_transaction(signed_transaction)
                            print("transaktsioonide arv:", len(signedTransactionChain.chain))
                            if len(signedTransactionChain.chain) >= n_transactions:  # Vaata kas on kogunenud n transaktsiooni
                                signedTransactionChain.add_transaction(oneBitcoinTransactionToMyWallet())
                                currentBlockChain = readBlockChainFromFile()
                                latest_block = currentBlockChain.get_latest_block()
                                new_block_in_da_hood = startCreatingBlock(latest_block.nr + 1, signedTransactionChain, public_key, latest_block.hash)
                                print("new_block_in_da_hood",new_block_in_da_hood.to_string())
                                currentBlockChain.add_block(new_block_in_da_hood)
                                writeBlockChainToFile(currentBlockChain)




                    except BadSignatureError:
                        error_message = json.dumps({"errcode": 400, "errmsg": "Bad Signature Error"})
                        json_length = len(error_message)
                        headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % json_length
                        response = headers + error_message
                        self.request.sendall(response.encode())

                    transactions_file = open('transactions-' + sys.argv[1] + '.json', "w+")
                    transactions_file.write(signedTransactionChain.to_string())
                    transactions_file.close()

                    headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: plain/text\r\n\r\n' % 1
                    response = headers + "1"
                    self.request.sendall(response.encode())
                    # saada teistele transactioneid edasi client_blocks(received_transaction)
                    with open('peers-' + sys.argv[1] + '.json', 'r') as f:
                        json_data = json.load(f)
                        for peer in json_data['peers']:
                            ip, port = peer.split(':')
                            client_packet(ip, int(port), 'transaction', signed_transaction,
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

                    # transaction_message = signed_transaction_object.to_string()

                    response_message = json.dumps(
                        {"message": "Thanks! %s bitcoins are on the way." % transaction_json["sum"]})
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
    print("My private key is ", private_key.to_string())
    print("My public key is ", public_key.to_string())
    balance = 10
    host_ip = "localhost"
    n_transactions = 2

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
    print("taltechCoin:", taltechCoin.to_string())
    #  print(taltechCoin.get_latest_block().hash)
    blocks = open('blocks-' + sys.argv[1] + '.json', "w+")
    blocks.write(taltechCoin.to_string())
    blocks.close()

    print("blockchain from file:",readBlockChainFromFile().to_string())
    my_transactions = SignedTransactionChain([])

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
