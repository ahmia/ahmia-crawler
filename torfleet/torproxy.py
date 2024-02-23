"""
Opens HTTP proxy to ports ARG1
Traffic goes through Tor socks5 on 127.0.0.1:ARG2.
For crawling purposes overrides HTTP status code 500 to 200!

python torproxy.py HTTP_SERVER_PORT TOR_SOCKS_PORT
python torproxy.py 19050 9050

Test:

curl -x http://localhost:19050 \
http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/robots.txt
"""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

class TorProxyHandler(BaseHTTPRequestHandler):
    def forward_request(self, method):
        url = self.path
        proxies = {
            'http': f'socks5h://127.0.0.1:{tor_socks_port}',
            'https': f'socks5h://127.0.0.1:{tor_socks_port}',
        }

        try:
            # Select method based on the request and execute it using requests library with Tor as proxy
            if method == 'GET':
                response = requests.get(url, proxies=proxies)
            elif method == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                response = requests.post(url, data=post_data, proxies=proxies)
            else:
                self.send_error(405, 'Method Not Allowed')
                return

            # Override status code 500 to 200 for crawling purposes
            status_code = 200 if response.status_code == 500 else response.status_code
            self.send_response(status_code)

            # Filter out headers that shouldn't be blindly forwarded
            excluded_headers = ['Content-Length', 'Transfer-Encoding', 'Content-Encoding']
            for key, value in response.headers.items():
                if key not in excluded_headers:
                    self.send_header(key, value)

            # Indicate to the client that the connection will be closed after completing the request
            self.send_header('Connection', 'close')
            self.end_headers()

            # Send the response content
            self.wfile.write(response.content)
        except requests.RequestException as e:
            self.send_error(500, 'Internal Server Error: {}'.format(e))

    def do_GET(self):
        self.forward_request('GET')

    def do_POST(self):
        self.forward_request('POST')

def run(server_class=HTTPServer, handler_class=TorProxyHandler, port=19050):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Proxy to SOCKS5 bridge.')
    parser.add_argument('http_server_port', type=int, help='Port for the HTTP proxy to listen on.')
    parser.add_argument('tor_socks_port', type=int, help='SOCKS5 port to route traffic through.')
    args = parser.parse_args()

    # Global variable for the Tor SOCKS port
    tor_socks_port = args.tor_socks_port

    run(port=args.http_server_port)
