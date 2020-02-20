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

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)


    def handle(self):
        # self.request is the TCP socket connected to the client
        print("{} wrote:".format(self.client_address[0]))
        data = self.request.recv(1024).strip()
        data_list = data.decode().split('\n')

        get_path = data_list[0].split(' ')[1]
        if get_path == '/getpeers':
            app_json = json.dumps(self.get_peers())
            len_json = len(app_json)
            headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % len_json

            response = headers + app_json
            print(response)
            self.request.sendall(response.encode())
        else:
            greeting = 'Hello world!'
            len_greeting = len(greeting)

            headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: text/html\r\n\r\n' % len_greeting
            response = headers + greeting
            print(response)
            self.request.sendall(response.encode())

    def get_peers(self):
        json_data = {'peers': []}

        with open('peers-' + sys.argv[1] + '.txt', 'r') as lines:
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
    f = open('peers-' + sys.argv[1] + '.txt', "a")
    f.close()

    server.serve_forever()
