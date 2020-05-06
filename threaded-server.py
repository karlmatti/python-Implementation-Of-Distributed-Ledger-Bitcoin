import json
import sys
import threading
from time import time

from Block import Block
from Blockchain import Blockchain
from ThreadedTCPRequestHandler import ThreadedTCPRequestHandler
from ThreadedTCPServer import ThreadedTCPServer
from Transactions import Transactions
from client import client_peers

if __name__ == "__main__":

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
                #print("json_data")
                #print(json_data)
                for peer in json_data['peers']:
                    ip, port = peer.split(':')
                    #print("I have a fellow %s:%s" % (ip, port))
                    client_peers(ip, int(port), "127.0.0.1:" + sys.argv[1])

            prev = now
        else:
            pass
            # runs
