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

try:
    if len(sys.argv) == 3:
        HTTP_PROXY_PORT = int(sys.argv[1])
        SOCKS_PORT = int(sys.argv[2])
        print("HTTP proxy localhost:%d <---> SOCKS localhost:%d" % (HTTP_PROXY_PORT, SOCKS_PORT) )
    else:
        print("python3 http_tor_proxy.py <SOCKS_PORT> <HTTP_PROXY_PORT>")
        sys.exit()
except Exception as e:
    print( str(e) )
    sys.exit()

if sys.version_info < (3, 0):
    import urllib2
    import socks
    import socket
    import SocketServer
    import SimpleHTTPServer
    import urllib
    import urlparse
    from StringIO import StringIO
    from BaseHTTPServer import BaseHTTPRequestHandler
else:
    print("Supports only Python2!")
    sys.exit()

# Disasble send proxies date and server headers
def send_response(self, code, message=None):
    self.log_request(code)
    if message is None:
        if code in self.responses:
            message = self.responses[code][0]
        else:
            message = ''
    if self.request_version != 'HTTP/0.9':
        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, code, message))
    # self.send_header('Server', self.version_string())
    # self.send_header('Date', self.date_time_string())

BaseHTTPRequestHandler.send_response = send_response


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", SOCKS_PORT)

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

# patch the socket module
socket.socket = socks.socksocket
socket.create_connection = create_connection


# disable following redirections
class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response


class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_method(self, method):
        try:
            if method == 'GET':
                request = urllib2.Request(self.path, headers=self.headers)
            elif method == 'HEAD':
                request = urllib2.Request(self.path, headers=self.headers)
                request.get_method = lambda : 'HEAD'
            elif method == 'POST':
                length = int(self.headers.getheaders("Content-Length")[0])
                post_data = urlparse.parse_qsl(self.rfile.read(length))
                request = urllib2.Request(self.path, urllib.urlencode(post_data), headers=self.headers)
            else:
                raise urllib2.HTTPError(self.path, 501, "Not Implemented", dict(), self.wfile)
            opener = urllib2.build_opener(NoRedirection)
            response = opener.open(request)
        except urllib2.HTTPError as error:
            response = error
        code = response.code
        self.send_response(code)
        is_content_type_present = False

        # parse all received headers
        headers = dict()
        for header in response.headers.headers:
            if ': ' not in header:
                raise ValueError('Invalid header. ": " not presents in "%s".' % header.strip())
            try:
                key, value = header.rstrip().split(': ', 1)
            except ValueError:
                key = header.rstrip().replace(':', '', 1)
                value = ''
            if key not in headers:
                headers[key] = [value]
            else:
                headers[key].append(value)

        # process and send headers
        for key in headers:
            for value in headers[key]:
                # urllib2 processing chunked data by itself, we need just skip header
                if (key.lower() == 'transfer-encoding') and (value.lower() == 'chunked'):
                    continue

                # is encoding set?
                if key.lower() == 'content-type':
                    is_content_type_present = True

                # send header
                self.send_header(key, value)

        # set default encoding header, without it scrapy fails to encode page
        if not is_content_type_present:
            self.send_header('Content-Type','text/html; charset=UTF-8')

        self.end_headers()

        # send body of response
        self.copyfile(response, self.wfile)

        # debug output
        VERBOSE = False
        if VERBOSE:
            print('request headers:')
            print(request.headers)
            if method == 'POST':
                print('POST data:')
                print(post_data)
                print('encoded POST data:')
                print(urllib.urlencode(post_data))
            print("url = %s\nresponse_code = %s\nheaders:" % (self.path, code))
            print(headers)
            print('end headers\n')

    def do_GET(self):
        self.do_method('GET')

    def do_HEAD(self):
        self.do_method('HEAD')

    def do_POST(self):
        self.do_method('POST')

try:
    httpd = SocketServer.ForkingTCPServer(('', HTTP_PROXY_PORT), Proxy)
except socket.error as e:
    print('Error: %s' % e)
    exit()

try:
    print("Serving at port %d" % HTTP_PROXY_PORT)
    httpd.serve_forever()
except KeyboardInterrupt:
    print(" shutting down...")
    httpd.shutdown()
