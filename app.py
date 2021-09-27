import http.server
import socketserver
import urllib

PORT = 7000

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        print(self.headers)
        print(self.path)

        self.query_string = self.rfile.read(int(self.headers['Content-Length']))
        self.args = dict(urllib.parse.parse_qsl(self.query_string))
        
        print(self.args)


Handler = ServerHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Keyboard interrupt received: EXITING')
    finally:
        httpd.server_close()