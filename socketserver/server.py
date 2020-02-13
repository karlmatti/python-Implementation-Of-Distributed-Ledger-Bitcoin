# https://github.com/martinve/pyp2p/blob/master/server.py
import socketserver
import json
import sys


def get_servers():
    with open('servers.json', 'r') as f:
        return json.load(f)


class MyRequestHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """


    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))

        data_list = self.data.decode().split('\n')


        get_path = data_list[0].split(' ')[1]
        if get_path == '/getpeers':
            print(self.get_peers())
        self.request.sendall(self.data)

    def get_peers(self):
        json_data = {'peers': []}
        print('peers-'+sys.argv[1]+'.txt')
        with open('peers-'+sys.argv[1]+'.txt', 'r+') as lines:
            for line in lines:
                if ':' in line:
                    server = line.split(':')
                    json_data['peers'].append({server[0]: server[1]})


        return json_data


if __name__ == "__main__":
    HOST = "localhost"

    PORT = int(sys.argv[1])  # 4000 + random.randrange(4000)

    # Create the server
    server = socketserver.TCPServer((HOST, PORT), MyRequestHandler)

    print("Server started on port:", PORT)
    server.serve_forever()
