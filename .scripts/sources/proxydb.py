import requests
import os
import random
import concurrent.futures
import threading
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .base import ProxySource

class ProxyDB(ProxySource):
    def get_active_proxies(self):
        proxies_list = []
        # Assuming the script is run from the root of the repo
        base_dir = os.path.join(os.getcwd(), 'proxies', 'active')
        
        files = {
            'http.txt': 'http',
            'socks4.txt': 'socks4',
            'socks5.txt': 'socks5'
        }
        
        for filename, scheme in files.items():
            filepath = os.path.join(base_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        for line in f:
                            proxy = line.strip()
                            if not proxy: continue
                            
                            # Construct proxy dict for requests
                            proxy_url = f"{scheme}://{proxy}"
                            proxies_list.append({
                                'http': proxy_url,
                                'https': proxy_url
                            })
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    
        return proxies_list

    def fetch(self):
        url_base = "https://proxydb.net/"
        step = 15
        ua = UserAgent()
        
        active_proxies = self.get_active_proxies()
        if active_proxies:
            print(f"  Loaded {len(active_proxies)} active proxies for rotation.")
        else:
            print("  No active proxies found. Using direct connection.")
            # If no proxies, we can't really rotate, so we might just fail or use direct.
            # For now, let's assume we have proxies or just use 1 worker.
        
        # Threading setup
        self.current_offset = 0
        self.offset_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.failed_offsets = []
        self.offset_retries = {} # Track retries per offset
        self.results_lock = threading.Lock()
        
        # Stop condition for consecutive empty/failed pages
        self.consecutive_failures = 0
        self.failures_lock = threading.Lock()
        # Stop if we see too many consecutive empty pages or failures.
        # Since we have multiple threads, we might see a burst of empty pages at the end.
        self.failure_threshold = 20 
        
        # Use up to 50 threads, or number of proxies
        max_workers = min(len(active_proxies), 50) if active_proxies else 1
        if max_workers < 1: max_workers = 1
        
        print(f"  Starting {max_workers} worker threads...")
        
        def check_failures():
            with self.failures_lock:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.failure_threshold:
                    print(f"  Reached {self.consecutive_failures} consecutive empty pages. Stopping.")
                    self.stop_event.set()
                    return True
            return False

        def reset_failures():
            with self.failures_lock:
                self.consecutive_failures = 0

        def get_next_offset():
            with self.offset_lock:
                if self.stop_event.is_set():
                    return None
                
                while self.failed_offsets:
                    off = self.failed_offsets.pop(0)
                    # Check retry count
                    retries = self.offset_retries.get(off, 0)
                    if retries >= 3:
                        print(f"    Offset {off} failed too many times. Skipping.")
                        continue
                    self.offset_retries[off] = retries + 1
                    return off
                
                off = self.current_offset
                self.current_offset += step
                return off

        def worker():
            while not self.stop_event.is_set():
                offset = get_next_offset()
                if offset is None:
                    break
                
                # Select proxy
                current_proxy = random.choice(active_proxies) if active_proxies else None
                proxy_ip = current_proxy['http'].split('//')[-1] if current_proxy else "Direct"
                
                params = {"offset": offset}
                headers = {'User-Agent': ua.random}
                
                try:
                    # print(f"    Fetching offset {offset} via {proxy_ip}...")
                    resp = requests.get(url_base, params=params, headers=headers, proxies=current_proxy, timeout=15)
                    
                    if resp.status_code != 200:
                        # print(f"    Bad status {resp.status_code} on offset {offset}")
                        with self.offset_lock:
                            self.failed_offsets.append(offset)
                        continue

                    soup = BeautifulSoup(resp.text, 'html.parser')
                    rows = soup.select('table tbody tr')
                    
                    if not rows:
                        # Check if it's a block or actual end
                        if "No proxies found" in resp.text or "No results" in resp.text or not soup.select('table'):
                             # Likely end
                             self.stop_event.set()
                             return
                        else:
                             # Maybe captcha?
                             with self.offset_lock:
                                 self.failed_offsets.append(offset)
                             continue

                    count = 0
                    for row in rows:
                        cols = row.find_all('td')
                        if not cols: continue
                        
                        try:
                            a_tag = cols[0].find('a')
                            if not a_tag: continue
                            
                            href = a_tag.get('href')
                            if not href: continue
                            
                            if href.startswith('/'):
                                href = href[1:]
                                
                            parts = href.split('/')
                            if len(parts) < 2: continue
                            
                            ip = parts[0]
                            rest = parts[1]
                            
                            if '#' in rest:
                                port, protocol = rest.split('#')
                            else:
                                port = rest
                                protocol = cols[2].text.strip().lower()
                                
                            proxy = f"{ip}:{port}"
                            protocol = protocol.lower()
                            
                            with self.results_lock:
                                if 'socks4' in protocol: self.add_proxy('socks4', proxy)
                                elif 'socks5' in protocol: self.add_proxy('socks5', proxy)
                                elif 'http' in protocol: self.add_proxy('http', proxy)
                            count += 1
                        except Exception:
                            continue
                    
                    print(f"    Parsed {count} proxies from offset {offset}")
                    
                    if count > 0:
                        reset_failures()
                    else:
                        check_failures()
                    
                except Exception as e:
                    # print(f"    Error on offset {offset}: {e}")
                    with self.offset_lock:
                        self.failed_offsets.append(offset)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker) for _ in range(max_workers)]
            concurrent.futures.wait(futures)
                
        return self.proxies
