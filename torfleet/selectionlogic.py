import random
from urllib.parse import urlparse

urls = [
    "http://1111hx5prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/abv.txt", # Same proxyN to these
    "http://1111hx5prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/bar.txt", # Same proxyN to these
    "http://2222225prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/ABC/1", # ProxyA
    "http://2222225prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/BBB/2", # ProxyA
    "http://45tbhx5prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/foo.txt", # ProxyB
    "http://45tbhx5prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/bar.txt", # ProxyB
    "http://3322225prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/lol.txt", # ProxyC
    "http://4422225prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/lol.txt", # ProxyD
]

for url in urls:
    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc
    random.seed(domain) # A seed for randomness is the onion domain
    # List of proxies available
    tor_proxy_list = list( range(8080,8090) )
    # Always select the same proxy for the same onion address
    print( "Proxy is localhost:%d" % random.choice(tor_proxy_list) )
