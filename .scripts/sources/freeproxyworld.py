import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .base import ProxySource

class FreeProxyWorld(ProxySource):
    def fetch(self):
        base_url = "https://www.freeproxy.world/"
        ua = UserAgent()
        page = 1
        
        while True:
            url = f"{base_url}?page={page}"
            headers = {'User-Agent': ua.random}
            
            try:
                print(f"  Fetching FreeProxyWorld page {page}...")
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    print(f"  Failed to fetch page {page} (Status: {resp.status_code})")
                    break
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                table = soup.find('table')
                if not table:
                    print("  No table found.")
                    break
                
                rows = table.find_all('tr')
                if len(rows) <= 1: 
                    print("  Table empty.")
                    break
                
                count = 0
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) < 6:
                        continue
                    
                    ip = cols[0].get_text(strip=True)
                    port = cols[1].get_text(strip=True)
                    protocol_str = cols[5].get_text(strip=True).lower()
                    
                    proxy = f"{ip}:{port}"
                    
                    if 'socks4' in protocol_str:
                        self.add_proxy('socks4', proxy)
                    elif 'socks5' in protocol_str:
                        self.add_proxy('socks5', proxy)
                    elif 'http' in protocol_str:
                        self.add_proxy('http', proxy)
                    
                    count += 1
                
                print(f"    Found {count} proxies on page {page}.")
                
                if count == 0:
                    break
                
                # Optional: Check for "Next" button to stop early if no more pages
                # But the hard limit handles the infinite loop case.
                    
                page += 1
                
            except Exception as e:
                print(f"Error fetching FreeProxyWorld page {page}: {e}")
                break
                
        return self.proxies
