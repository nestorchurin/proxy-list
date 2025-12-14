import requests
from .base import ProxySource

class GeoNode(ProxySource):
    def fetch(self):
        url = "https://proxylist.geonode.com/api/proxy-list"
        limit = 500
        page = 1
        max_pages = 10
        
        while page <= max_pages:
            params = {
                "limit": limit,
                "page": page,
                "sort_by": "lastChecked",
                "sort_type": "desc"
            }
            
            try:
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
                print(f"Error fetching GeoNode page {page}: {e}")
                break
                
        return self.proxies
