import random
from urllib.parse import urlparse

urls = [
    "http://2222222222222222.onion/foo.txt",  # Same proxyN to these
    "http://2222222222222222.onion/bar.txt",  # Same proxyN to these
    "http://2222222222222223.onion/lol.txt",  # ProxyA
    "http://2222222222222224.onion/lol.txt",  # ProxyB etc.
    "http://45tbhx5prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/foo.txt",
    "http://45tbhx5prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawkid.onion/bar.txt",
    "http://45tbhx5prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawki5.onion/lol.txt",
    "http://45tbhx5prlejzjgn36nqaxqb6qnm73pbohuvqkpxz2zowh57bxqawki7.onion/lol.txt",
]

for u in urls:
    parsed_uri = urlparse(u)
    hash = '{uri.netloc}'.format(uri=parsed_uri).replace(".onion", "")
    random.seed(hash)  # A seed for randomness is the onion domain
    # List of proxies available
    tor_proxy_list = list(range(8080, 8090))
    # Always select the same proxy for the same onion address
    print("Proxy is localhost:%d" % random.choice(tor_proxy_list))
