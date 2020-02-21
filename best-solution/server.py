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

        print("%s:%s sent:" % (self.client_address[0], self.client_address[1]))

        data = self.request.recv(1024).strip()
        data_list = data.decode().split('\n')
        request_method = data_list[0].split(' ')[0]
        request_path = data_list[0].split(' ')[1]

        if request_method == 'GET':

            if request_path == '/getpeers':
                app_json = json.dumps(self.get_peers())
                len_json = len(app_json)
                headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: json/application\r\n\r\n' % len_json
                response = headers + app_json
                self.request.sendall(response.encode())

        elif request_method == 'POST':

            if request_path == '/':

                json_data = json.loads(data_list[-1])
                f = open('peers-' + sys.argv[1] + '.txt', "a")

                for ip in json_data['peers']:
                    f.write(ip + '\n')

                f.close()
                body = 'Peers added successfully!'
                len_body = len(body)
                headers = 'HTTP/1.1 200 OK\r\nContent-Length: %s\r\nContent-Type: text/html\r\n\r\n' % len_body
                response = headers + body
                print(response)
                self.request.sendall(response.encode())

    def get_peers(self):
        json_data = {'peers': []}

        with open('peers-' + sys.argv[1] + '.txt', 'r') as lines:
            for line in lines:
                if ':' in line:
                    line = line.strip('\n')
                    server = line.split(':')
                    json_data['peers'].append({server[0]: server[1]})

        return json_data


if __name__ == "__main__":
    HOST = "localhost"

    PORT = int(sys.argv[1])

    # Create the server
    server = socketserver.TCPServer((HOST, PORT), MyRequestHandler)

    print("Server started on port:", PORT)
    f = open('peers-' + sys.argv[1] + '.txt', "a")
    f.close()

    server.serve_forever()
