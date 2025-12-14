import requests
import os
import concurrent.futures
import pkgutil
import importlib
import inspect
import sources
from sources.base import ProxySource

# Configuration
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "proxies")
CLEAN_DIR = os.path.join(BASE_DIR, "clean")
ACTIVE_DIR = os.path.join(BASE_DIR, "active")

def save_proxies_from_source(source_name, proxies_dict):
    """Saves a dict of proxies to proxies/<source_name>/<protocol>.txt"""
    directory = os.path.join(BASE_DIR, source_name)
    
    # Clear directory first
    if os.path.exists(directory):
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))
    os.makedirs(directory, exist_ok=True)
    
    total_count = 0
    for protocol, proxy_list in proxies_dict.items():
        if not proxy_list:
            continue
            
        # Remove duplicates within the list
        unique_proxies = list(set(proxy_list))
        
        filename = os.path.join(directory, f"{protocol}.txt")
        with open(filename, 'w') as f:
            f.write('\n'.join(unique_proxies) + '\n')
        
        total_count += len(unique_proxies)
        
    print(f"  Saved {total_count} proxies from {source_name}")

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
            # Skip clean, active, and any non-directory
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
    test_urls = [
        'http://httpbin.org/ip',
        'https://api.ipify.org?format=json',
        'https://ifconfig.me/ip'
    ]
    proxies = {
        'http': f'{protocol}://{proxy}',
        'https': f'{protocol}://{proxy}'
    }
    for url in test_urls:
        try:
            resp = requests.get(url, proxies=proxies, timeout=timeout)
            if resp.status_code == 200:
                return proxy
        except Exception:
            continue
    return None

def check_proxies_liveness():
    print("\nChecking proxies liveness...")
    os.makedirs(ACTIVE_DIR, exist_ok=True)
    
    timeout = 30
    max_workers = 50
    
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

def load_proxy_sources():
    source_instances = []
    # Iterate over all modules in the 'sources' package
    for _, name, _ in pkgutil.iter_modules(sources.__path__, sources.__name__ + "."):
        if name.endswith('.base'): continue
        
        try:
            module = importlib.import_module(name)
            # Find the class that inherits from ProxySource
            for _, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, ProxySource) and 
                    obj is not ProxySource):
                    
                    source_name = name.split('.')[-1]
                    source_instances.append((source_name, obj()))
                    break 
        except Exception as e:
            print(f"Error loading module {name}: {e}")
    return source_instances

def main():
    # 1. Fetch from all sources
    sources_list = load_proxy_sources()
    print(f"Loaded {len(sources_list)} sources: {[n for n, _ in sources_list]}")

    for name, source in sources_list:
        print(f"Fetching from {name}...")
        try:
            proxies = source.fetch()
            save_proxies_from_source(name, proxies)
        except Exception as e:
            print(f"Error running {name}: {e}")
            
    # 2. Deduplicate
    deduplicate_proxies()
    
    # 3. Check
    check_proxies_liveness()

if __name__ == "__main__":
    main()
