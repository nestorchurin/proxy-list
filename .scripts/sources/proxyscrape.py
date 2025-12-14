import requests
from .base import ProxySource

class ProxyScrape(ProxySource):
    def fetch(self):
        urls = [
            ('socks4', "http://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&protocol=socks4&proxy_format=ipport&format=text&timeout=20000"),
            ('socks5', "http://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&protocol=socks5&proxy_format=ipport&format=text&timeout=20000"),
            ('http', "http://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&protocol=http&proxy_format=ipport&format=text&timeout=20000")
        ]
        
        for protocol, url in urls:
            try:
                resp = requests.get(url, timeout=20)
                if resp.status_code == 200:
                    proxies = [p.strip() for p in resp.text.splitlines() if p.strip()]
                    self.proxies[protocol].extend(proxies)
            except Exception as e:
                print(f"Error fetching ProxyScrape {protocol}: {e}")
                
        return self.proxies
