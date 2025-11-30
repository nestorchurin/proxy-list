import requests
import os
import concurrent.futures
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json

# Configuration
BASE_DIR = "proxies"
CLEAN_DIR = os.path.join(BASE_DIR, "clean")
ACTIVE_DIR = os.path.join(BASE_DIR, "active")
CONFIG_FILE = "proxy_sources.json"

ua = UserAgent()

def get_headers():
    return {'User-Agent': ua.random}

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_proxies(source, protocol, proxies):
    """Saves a list of proxies to proxies/<source>/<protocol>.txt"""
    if not proxies:
        return
    
    directory = os.path.join(BASE_DIR, source)
    os.makedirs(directory, exist_ok=True)
    
    filename = os.path.join(directory, f"{protocol}.txt")
    
    with open(filename, 'a') as f:
        f.write('\n'.join(proxies) + '\n')

def clear_source_dir(source):
    """Clears the source directory before starting a new fetch session"""
    directory = os.path.join(BASE_DIR, source)
    if os.path.exists(directory):
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))

def fetch_text_list(source_config):
    name = source_config['name']
    print(f"Fetching from {name} (Text List)...")
    clear_source_dir(name)
    
    for item in source_config['urls']:
        protocol = item['protocol']
        url = item['url']
        try:
            resp = requests.get(url, headers=get_headers(), timeout=20)
            if resp.status_code == 200:
                proxies = [p.strip() for p in resp.text.splitlines() if p.strip()]
                save_proxies(name, protocol, proxies)
                print(f"  Fetched {len(proxies)} {protocol} proxies.")
        except Exception as e:
            print(f"  Error fetching {url}: {e}")

def fetch_json_api(source_config):
    name = source_config['name']
    print(f"Fetching from {name} (JSON API)...")
    clear_source_dir(name)
    
    url = source_config['url']
    params = source_config['params'].copy()
    pagination = source_config.get('pagination')
    mapping = source_config['mapping']
    
    page_param = pagination['param']
    current_val = pagination['start']
    limit = pagination['limit']
    
    count = 0
    while True:
        params[page_param] = current_val
        try:
            resp = requests.get(url, params=params, headers=get_headers(), timeout=20)
            try:
                data = resp.json()
            except json.JSONDecodeError:
                print(f"  Error decoding JSON from {name}")
                break

            # Navigate to the list using list_key (supports dot notation e.g. "data.items")
            items = data
            if mapping.get('list_key'):
                for key in mapping['list_key'].split('.'):
                    if isinstance(items, dict):
                        items = items.get(key, [])
                    else:
                        items = []
                        break
            
            if not items:
                break
                
            collected = {'http': [], 'socks4': [], 'socks5': []}
            
            for item in items:
                ip = item.get(mapping['ip'])
                port = item.get(mapping['port'])
                
                if not ip or not port: continue
                
                proxy = f"{ip}:{port}"
                
                protocols = item.get(mapping['protocols'], [])
                if isinstance(protocols, str):
                    protocols = [protocols]
                
                for proto in protocols:
                    p_lower = proto.lower()
                    if 'socks4' in p_lower: collected['socks4'].append(proxy)
                    elif 'socks5' in p_lower: collected['socks5'].append(proxy)
                    elif 'http' in p_lower or 'https' in p_lower: collected['http'].append(proxy)
            
            for proto, proxies in collected.items():
                if proxies:
                    save_proxies(name, proto, proxies)
            
            print(f"  Page {current_val} done. Found {len(items)} items.")
            
            count += 1
            if count >= limit:
                break
            
            current_val += 1
            
        except Exception as e:
            print(f"  Error fetching {name} page {current_val}: {e}")
            break

def fetch_html_table(source_config):
    name = source_config['name']
    print(f"Fetching from {name} (HTML Table)...")
    clear_source_dir(name)
    
    url_base = source_config['url']
    params = source_config['params'].copy()
    pagination = source_config.get('pagination')
    
    offset_param = pagination['param']
    current_val = pagination['start']
    step = pagination.get('step', 1)
    limit = pagination['limit']
    
    while True:
        params[offset_param] = current_val
        
        try:
            resp = requests.get(url_base, params=params, headers=get_headers(), timeout=20)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            rows = soup.select('table tbody tr')
            if not rows:
                break
                
            collected = {'http': [], 'socks4': [], 'socks5': []}
            
            for row in rows:
                cols = row.find_all('td')
                if not cols: continue
                
                proxy = cols[0].text.strip() # IP:Port
                protocol_str = cols[4].text.strip().lower()
                
                if 'socks4' in protocol_str: collected['socks4'].append(proxy)
                elif 'socks5' in protocol_str: collected['socks5'].append(proxy)
                elif 'http' in protocol_str: collected['http'].append(proxy)
            
            for proto, proxies in collected.items():
                if proxies:
                    save_proxies(name, proto, proxies)
            
            print(f"  Offset {current_val} done.")
            
            current_val += step
            if current_val > limit:
                break
                
        except Exception as e:
            print(f"  Error fetching {name}: {e}")
            break

def deduplicate_proxies():
    print("\nDeduplicating proxies...")
    os.makedirs(CLEAN_DIR, exist_ok=True)
    
    # Clear clean dir
    for f in os.listdir(CLEAN_DIR):
        os.remove(os.path.join(CLEAN_DIR, f))
    
    for proto in ['http', 'socks4', 'socks5']:
        all_proxies = set()
        
        # Walk through all source folders
        for source in os.listdir(BASE_DIR):
            source_path = os.path.join(BASE_DIR, source)
            if not os.path.isdir(source_path) or source in ['clean', 'active']:
                continue
                
            file_path = os.path.join(source_path, f"{proto}.txt")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    for line in f:
                        p = line.strip()
                        if p: all_proxies.add(p)
        
        if all_proxies:
            clean_file = os.path.join(CLEAN_DIR, f"{proto}.txt")
            with open(clean_file, 'w') as f:
                f.write('\n'.join(all_proxies) + '\n')
            print(f"Saved {len(all_proxies)} unique {proto} proxies to {clean_file}")

def check_single_proxy(proxy, protocol, timeout):
    url = 'http://httpbin.org/ip'
    proxies = {
        'http': f'{protocol}://{proxy}',
        'https': f'{protocol}://{proxy}'
    }
    try:
        resp = requests.get(url, proxies=proxies, timeout=timeout)
        if resp.status_code == 200:
            return proxy
    except:
        pass
    return None

def check_proxies_liveness(settings):
    print("\nChecking proxies liveness...")
    os.makedirs(ACTIVE_DIR, exist_ok=True)
    
    timeout = settings.get('check_timeout', 30)
    max_workers = settings.get('max_workers', 50)
    
    print(f"Settings: Timeout={timeout}s, Workers={max_workers}")
    
    for proto in ['http', 'socks4', 'socks5']:
        clean_file = os.path.join(CLEAN_DIR, f"{proto}.txt")
        if not os.path.exists(clean_file):
            continue
            
        print(f"Checking {proto} proxies...")
        with open(clean_file, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
            
        working = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {executor.submit(check_single_proxy, p, proto, timeout): p for p in proxies}
            
            completed = 0
            total = len(proxies)
            for future in concurrent.futures.as_completed(future_to_proxy):
                completed += 1
                if completed % 50 == 0:
                    print(f"  Checked {completed}/{total} {proto} proxies...")
                    
                result = future.result()
                if result:
                    working.append(result)
        
        if working:
            active_file = os.path.join(ACTIVE_DIR, f"{proto}.txt")
            with open(active_file, 'w') as f:
                f.write('\n'.join(working) + '\n')
            print(f"Saved {len(working)} active {proto} proxies to {active_file}")
        else:
            print(f"No active {proto} proxies found.")

def main():
    config = load_config()
    
    # 1. Fetch
    for source in config['sources']:
        if source['type'] == 'text_list':
            fetch_text_list(source)
        elif source['type'] == 'json_api':
            fetch_json_api(source)
        elif source['type'] == 'html_table':
            fetch_html_table(source)
            
    # 2. Deduplicate
    deduplicate_proxies()
    
    # 3. Check
    check_proxies_liveness(config['settings'])

if __name__ == "__main__":
    main()
