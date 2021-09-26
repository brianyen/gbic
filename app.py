import http.server
import socketserver

PORT = 7000

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        print(self.headers)
        print(self.path)

Handler = ServerHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()