"""
Opens HTTP proxy to port 14444
Traffic goes through socks5 on 127.0.0.1:9050 which is Tor
For crawling purposes overrides HTTP status code 500 to 200!

python3 http_tor_proxy.py

Test:
curl -x http://localhost:14444 http://msydqstlz2kzerdg.onion/
"""

import socks
import socket
def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)

# patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection

import socketserver
import http.server
import urlparse2
import urllib
import urllib.request

PORT = 14444

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print( "GET " + self.path )
        # Catch HTTP errors
        try:
            response = urllib.request.urlopen(self.path)
        except urllib.HTTPError as error:
            response = error
            # Change HTTP error code 500 to 200
            if response.code == 500:
                response.code = 200
        self.copyfile(response, self.wfile)
    def do_POST(self):
        print( "POST " + self.path )
        length = int(self.headers.getheaders("Content-Length")[0])
        post_data = urlparse.parse_qs(self.rfile.read(length))
        # Catch HTTP errors
        try:
            post_data = urllib.urlencode(post_data)
            response = urllib.request.urlopen(self.path, post_data)
        except urllib.HTTPError as error:
            response = error
            # Change HTTP error code 500 to 200
            if response.code == 500:
                response.code = 200
        self.copyfile(response, self.wfile)

httpd = socketserver.ForkingTCPServer(('', PORT), Proxy)
print("Serving at port %d" % PORT)
httpd.serve_forever()
