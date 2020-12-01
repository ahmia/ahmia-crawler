"""
Opens HTTP proxy to ports ARG1
Traffic goes through socks5 on 127.0.0.1:ARG2
which are Tor clients.
For crawling purposes overrides HTTP status code 500 to 200!

python http_tor_proxy.py 15000 19050

Test:
curl -x http://localhost:15000 http://msydqstlz2kzerdg.onion/
"""

import sys
import socks
import socket

try:
    if len(sys.argv) == 3:
        HTTP_PROXY_PORT = int(sys.argv[1])
        SOCKS_PORT = int(sys.argv[2])
        print("HTTP proxy %d <---> SOCKS %d" % (HTTP_PROXY_PORT, SOCKS_PORT))
        print("Opening HTTP proxy localhost:%d" % HTTP_PROXY_PORT)
    else:
        print("python3 http_tor_proxy.py <SOCKS_PORT> <HTTP_PROXY_PORT>")
        sys.exit()
except Exception as e:
    print(str(e))
    sys.exit()


def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", SOCKS_PORT)

# patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection

if sys.version_info >= (3, 0):
    import socketserver
    import http.server
    import urllib
    import urllib.parse
    from urllib.request import urlopen
    HTTPError = urllib.request.HTTPError
    HTTPHandler = http.server.SimpleHTTPRequestHandler
if sys.version_info < (3, 0):
    import SocketServer as socketserver
    from SimpleHTTPServer import SimpleHTTPRequestHandler as HTTPHandler
    import urllib2 as urllib
    from urllib2 import urlopen
    from urlparse import urlparse
    HTTPError = urllib.HTTPError


class Proxy(HTTPHandler):
    def do_GET(self):
        print("GET", self.path)

        # Catch HTTP errors
        try:
            response = urlopen(self.path)
        except HTTPError as error:
            response = error
            # Change HTTP error code 500 to 200
            if response.code == 500:
                response.code = 200
        self.copyfile(response, self.wfile)

    def do_POST(self):
        print("POST", self.path)

        length = int(self.headers.getheaders("Content-Length")[0])
        post_data = urllib.parse.parse_qs(self.rfile.read(length))
        # Catch HTTP errors
        try:
            post_data = urllib.parse.urlencode(post_data)
            response = urlopen(self.path, post_data)
        except HTTPError as error:
            response = error
            # Change HTTP error code 500 to 200
            if response.code == 500:
                response.code = 200
        self.copyfile(response, self.wfile)


httpd = socketserver.ForkingTCPServer(('', HTTP_PROXY_PORT), Proxy)
print("Serving at port %d" % HTTP_PROXY_PORT)
httpd.serve_forever()
