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
