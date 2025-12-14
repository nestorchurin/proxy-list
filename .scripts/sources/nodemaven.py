import requests
from .base import ProxySource

class NodeMaven(ProxySource):
    def fetch(self):
        url = "https://nodemaven.com/wp-json/proxy-list/v1/proxies"
        page = 1
        
        while True:
            params = {
                "page": page,
                "per_page": 500
            }
            
            try:
                print(f"  Fetching NodeMaven page {page}...")
                resp = requests.get(url, params=params, timeout=20)
                data = resp.json()
                items = data.get('data', [])
                
                if not items:
                    break
                    
                for item in items:
                    ip = item.get('ip')
                    port = item.get('port')
                    protocols = item.get('protocols', [])
                    
                    if not ip or not port: continue
                    
                    proxy = f"{ip}:{port}"
                    
                    # NodeMaven sometimes returns protocols as a list of dicts or strings, 
                    # but based on previous config it seemed to be a list of strings or similar.
                    # Let's assume list of strings based on previous generic implementation.
                    
                    for proto in protocols:
                        p_lower = str(proto).lower() # Ensure string
                        if 'socks4' in p_lower: self.add_proxy('socks4', proxy)
                        elif 'socks5' in p_lower: self.add_proxy('socks5', proxy)
                        elif 'http' in p_lower or 'https' in p_lower: self.add_proxy('http', proxy)
                
                page += 1
                
            except Exception as e:
                print(f"Error fetching NodeMaven page {page}: {e}")
                break
                
        return self.proxies
