import os

def count_lines(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r') as f:
        return sum(1 for line in f if line.strip())

def update_readme():
    active_http = count_lines('proxies/active/http.txt')
    active_socks4 = count_lines('proxies/active/socks4.txt')
    active_socks5 = count_lines('proxies/active/socks5.txt')
    
    clean_http = count_lines('proxies/clean/http.txt')
    clean_socks4 = count_lines('proxies/clean/socks4.txt')
    clean_socks5 = count_lines('proxies/clean/socks5.txt')

    readme_content = f"""# Free Proxy List

![GitHub last commit](https://img.shields.io/github/last-commit/nestorchurin/proxy-list)
![License](https://img.shields.io/github/license/nestorchurin/proxy-list)

Automated free proxy list, updated daily.
Contains **HTTP**, **SOCKS4**, and **SOCKS5** proxies.

## 📊 Statistics (Live / Total Unique)

| Protocol | Active (Live) | Unique (Total) | Download Active | Download Unique |
|----------|---------------|----------------|-----------------|-----------------|
| **HTTP** | {active_http} | {clean_http} | [📥 Download](proxies/active/http.txt) | [📥 Download](proxies/clean/http.txt) |
| **SOCKS4** | {active_socks4} | {clean_socks4} | [📥 Download](proxies/active/socks4.txt) | [📥 Download](proxies/clean/socks4.txt) |
| **SOCKS5** | {active_socks5} | {clean_socks5} | [📥 Download](proxies/active/socks5.txt) | [📥 Download](proxies/clean/socks5.txt) |

## 🚀 Usage

### Raw Links (Active Proxies)
- **HTTP**: `https://raw.githubusercontent.com/nestorchurin/proxy-list/main/proxies/active/http.txt`
- **SOCKS4**: `https://raw.githubusercontent.com/nestorchurin/proxy-list/main/proxies/active/socks4.txt`
- **SOCKS5**: `https://raw.githubusercontent.com/nestorchurin/proxy-list/main/proxies/active/socks5.txt`

## 🛠 How it works
This repository uses a Python script to:
1. Scrape free proxies from multiple public sources.
2. Deduplicate and clean the lists.
3. Check each proxy for liveness.
4. Update this repository automatically.

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("README.md updated with latest stats.")

if __name__ == "__main__":
    update_readme()
