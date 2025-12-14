import requests
from .base import ProxySource

class Proxy911(ProxySource):
    def fetch(self):
        base_url = "https://www.911proxy.com/web_v1/free-proxy/list"
        page = 1
        page_size = 500
        
        while True:
            params = {
                "page_size": page_size,
                "page": page
            }
            
            try:
                print(f"  Fetching 911proxy page {page}...")
                resp = requests.get(base_url, params=params, timeout=15)
                
                if resp.status_code != 200:
                    print(f"  Failed to fetch page {page} (Status: {resp.status_code})")
                    break
                
                data = resp.json()
                if data.get("code") != 200:
                    print(f"  API Error: {data.get('msg')}")
                    break
                
                proxy_list = data.get("data", {}).get("list", [])
                if not proxy_list:
                    print("  No more proxies found.")
                    break
                
                count = 0
                for item in proxy_list:
                    ip = item.get("ip")
                    port = item.get("port")
                    protocol_code = item.get("protocol")
                    
                    if not ip or not port: continue
                    
                    proxy = f"{ip}:{port}"
                    
                    # Protocol mapping (inferred)
                    # 1: HTTP
                    # 2: HTTPS (treat as HTTP)
                    # 4: SOCKS4
                    # 8: SOCKS5
                    
                    # It might be a bitmask, so we check bits
                    
                    if protocol_code & 4:
                        self.add_proxy('socks4', proxy)
                    if protocol_code & 8:
                        self.add_proxy('socks5', proxy)
                    if protocol_code & 1 or protocol_code & 2:
                        self.add_proxy('http', proxy)
                        
                    count += 1
                
                print(f"    Found {count} proxies on page {page}.")
                
                # If we got fewer items than page_size, it's likely the last page
                if len(proxy_list) < page_size:
                    break
                    
                page += 1
                
            except Exception as e:
                print(f"Error fetching 911proxy page {page}: {e}")
                break
                
        return self.proxies
