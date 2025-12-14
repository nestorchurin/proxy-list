import os

# Define base paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROXIES_DIR = os.path.join(BASE_DIR, 'proxies')
README_PATH = os.path.join(BASE_DIR, 'README.md')

def count_lines(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(full_path):
        return 0
    with open(full_path, 'r') as f:
        return sum(1 for line in f if line.strip())

def read_file_content(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(full_path):
        return ""
    with open(full_path, 'r') as f:
        return f.read().strip()

def update_readme():
    active_http = count_lines('proxies/active/http.txt')
    active_socks4 = count_lines('proxies/active/socks4.txt')
    active_socks5 = count_lines('proxies/active/socks5.txt')
    
    clean_http = count_lines('proxies/clean/http.txt')
    clean_socks4 = count_lines('proxies/clean/socks4.txt')
    clean_socks5 = count_lines('proxies/clean/socks5.txt')

    base_template = read_file_content('.scripts/sources/base.py')
    example_source = read_file_content('.scripts/sources/proxyscrape.py')

    readme_content = f"""# 🌐 Free Proxy List

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
| **HTTP** | {active_http} | {clean_http} | [📥 Download](proxies/active/http.txt) | [📥 Download](proxies/clean/http.txt) |
| **SOCKS4** | {active_socks4} | {clean_socks4} | [📥 Download](proxies/active/socks4.txt) | [📥 Download](proxies/clean/socks4.txt) |
| **SOCKS5** | {active_socks5} | {clean_socks5} | [📥 Download](proxies/active/socks5.txt) | [📥 Download](proxies/clean/socks5.txt) |

## 🤝 How to Contribute
We welcome contributions! If you know a good source of free proxies, you can add it to the scraper.

> **Important:** We accept direct sources (APIs, websites, HTML tables). We **do not** accept other GitHub repositories or aggregators that simply re-upload scraped lists. We want to fetch from the source, not from another scraper.

### Adding a New Proxy Source
1.  Navigate to `.scripts/sources/`.
2.  Create a new file (e.g., `mysource.py`).
3.  Inherit from `ProxySource` and implement the `fetch()` method.

**Base Template (`base.py`):**
```python
{base_template}
```

**Example Implementation (`proxyscrape.py`):**
```python
{example_source}
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
"""
    
    with open(README_PATH, 'w') as f:
        f.write(readme_content)
    print("README.md updated with latest stats.")

if __name__ == "__main__":
    update_readme()
