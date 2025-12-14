import requests
from .base import ProxySource

class RoundProxies(ProxySource):
    def fetch(self):
        url = "https://roundproxies.com/api/get-free-proxies/"
        limit = 500
        page = 1
        
        while True:
            params = {
                "limit": limit,
                "page": page,
                "sort_by": "lastChecked",
                "sort_type": "desc"
            }
            
            try:
                print(f"  Fetching RoundProxies page {page}...")
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
                    
                    for proto in protocols:
                        p_lower = proto.lower()
                        if 'socks4' in p_lower: self.add_proxy('socks4', proxy)
                        elif 'socks5' in p_lower: self.add_proxy('socks5', proxy)
                        elif 'http' in p_lower or 'https' in p_lower: self.add_proxy('http', proxy)
                
                page += 1
                
            except Exception as e:
                print(f"Error fetching RoundProxies page {page}: {e}")
                break
                
        return self.proxies
