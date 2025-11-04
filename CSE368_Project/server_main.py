from flask import Flask
import socketserver


class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route("GET", "/hello", hello_path, True)
        # TODO: Add your routes here

        super().__init__(request, client_address, server)

    def handle(self):

        received_data = self.request.recv(16384)
        request = Request(received_data)

        # buffer till entire request is read
        if (len(received_data) != 0 and "Content-Length" in request.headers):
            while (len(request.body) < int(request.headers["Content-Length"])):
                data = self.request.recv(16384)
                request.body += data
                received_data += data

        print(self.client_address)
        print("--- received data ---")
        print(request.path)
        print(received_data)
        print("--- end of data ---\n\n")

        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()
