import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .base import ProxySource

class ProxyDB(ProxySource):
    def fetch(self):
        url_base = "https://proxydb.net/"
        offset = 0
        step = 15
        limit = 200
        ua = UserAgent()
        
        while offset <= limit:
            params = {"offset": offset}
            headers = {'User-Agent': ua.random}
            
            try:
                resp = requests.get(url_base, params=params, headers=headers, timeout=20)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                rows = soup.select('table tbody tr')
                if not rows:
                    break
                    
                for row in rows:
                    cols = row.find_all('td')
                    if not cols: continue
                    
                    proxy = cols[0].text.strip() # IP:Port
                    protocol_str = cols[4].text.strip().lower()
                    
                    if 'socks4' in protocol_str: self.add_proxy('socks4', proxy)
                    elif 'socks5' in protocol_str: self.add_proxy('socks5', proxy)
                    elif 'http' in protocol_str: self.add_proxy('http', proxy)
                
                offset += step
                
            except Exception as e:
                print(f"Error fetching ProxyDB offset {offset}: {e}")
                break
                
        return self.proxies
