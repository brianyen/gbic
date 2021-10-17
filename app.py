import http.server
import socketserver
import urllib
import re
import numpy as np

import converter

PORT = 7000

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):
        print(self.headers)
        print(self.path)

        self.query_string = self.rfile.read(int(self.headers['Content-Length']))
        self.args = dict(urllib.parse.parse_qsl(self.query_string))
        
        print(self.args)
        url = self.args[b'url'].decode('ascii')
        url_short = re.sub('^https?://', '', url)

        out_dir = urllib.parse.quote_plus(url_short)
        out_dir = out_dir.replace("%", "-")

        print(out_dir)

        converter.main(url, out_dir)


Handler = ServerHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Keyboard interrupt received: EXITING')
    finally:
        httpd.server_close()