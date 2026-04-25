import os
import json
from pathlib import Path


class ProxyManager:
    def __init__(self):
        self.config_dir = Path.home() / ".vdownloader"
        self.config_dir.mkdir(exist_ok=True)
        self.proxies_file = self.config_dir / "proxies.json"
        self.proxies = self.load_proxies()
    
    def load_proxies(self):
        if self.proxies_file.exists():
            try:
                with open(self.proxies_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_proxies(self):
        with open(self.proxies_file, 'w') as f:
            json.dump(self.proxies, f, indent=2)
    
    def add_proxy(self, name, proxy_url):
        self.proxies[name] = proxy_url
        self.save_proxies()
    
    def remove_proxy(self, name):
        if name in self.proxies:
            del self.proxies[name]
            self.save_proxies()
    
    def get_proxy(self, name):
        return self.proxies.get(name, None)
    
    def get_all_proxies(self):
        return list(self.proxies.items())
    
    def get_proxy_names(self):
        return list(self.proxies.keys())