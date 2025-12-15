# 🌐 Free Proxy List

![GitHub last commit](https://img.shields.io/github/last-commit/nestorchurin/proxy-list)
![License](https://img.shields.io/github/license/nestorchurin/proxy-list)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/nestorchurin/proxy-list/update_proxies.yml?label=Auto-Update)

A fully automated, open-source repository providing fresh, checked, and deduplicated free proxies.
Updated **every 6 hours** via GitHub Actions.

## 🎯 Who is this for?
This project is designed for developers, researchers, and enthusiasts who need free proxies for:
*   🕷️ **Web Scraping**: Rotating IPs to avoid rate limits.
*   🛡️ **Privacy Testing**: Checking anonymity and headers.
*   🌍 **Geo-Bypassing**: Accessing content restricted by region (use with caution).
*   🧪 **Development**: Testing applications with proxy support.

> **Note:** These are *public* free proxies. They are not recommended for sensitive data or high-stability requirements.

## 📊 Live Statistics

| Protocol | Active (Live) | Unique (Total) | Download Active | Download Unique |
|----------|---------------|----------------|-----------------|-----------------|
| **HTTP** | 30 | 3053 | [📥 Download](proxies/active/http.txt) | [📥 Download](proxies/clean/http.txt) |
| **SOCKS4** | 110 | 6794 | [📥 Download](proxies/active/socks4.txt) | [📥 Download](proxies/clean/socks4.txt) |
| **SOCKS5** | 1 | 1338 | [📥 Download](proxies/active/socks5.txt) | [📥 Download](proxies/clean/socks5.txt) |

## 🤝 How to Contribute
We welcome contributions! If you know a good source of free proxies, you can add it to the scraper.

> **Important:** We accept direct sources (APIs, websites, HTML tables). We **do not** accept other GitHub repositories or aggregators that simply re-upload scraped lists. We want to fetch from the source, not from another scraper.

### Adding a New Proxy Source
1.  Navigate to `.scripts/sources/`.
2.  Create a new file (e.g., `mysource.py`).
3.  Inherit from `ProxySource` and implement the `fetch()` method.

**Base Template (`base.py`):**
```python
from abc import ABC, abstractmethod

class ProxySource(ABC):
    def __init__(self):
        self.proxies = {'http': [], 'socks4': [], 'socks5': []}

    @abstractmethod
    def fetch(self):
        """
        Fetches proxies and returns a dictionary:
        {
            'http': ['ip:port', ...],
            'socks4': ['ip:port', ...],
            'socks5': ['ip:port', ...]
        }
        """
        pass

    def add_proxy(self, protocol, proxy):
        if protocol in self.proxies:
            self.proxies[protocol].append(proxy)
```

**Example Implementation (`proxyscrape.py`):**
```python
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
```

4.  Register your new source in `.scripts/proxy_manager.py` (it's auto-discovered!).
5.  Submit a **Pull Request**!

## 🛠 How it works
1.  **Fetch**: Scripts in `.scripts/sources/` scrape proxies from various public APIs and websites.
2.  **Clean**: Duplicates are removed across all sources.
3.  **Check**: Every proxy is tested against `httpbin.org` or similar services to ensure it's alive.
4.  **Deploy**: Results are pushed to this repo automatically.

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
