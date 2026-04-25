import os
import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict


BROWSER_PATHS = {
    'chrome': {
        'win': os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies'),
        'cookies_db': 'cookies',
    },
    'firefox': {
        'win': os.path.expanduser(r'~\AppData\Roaming\Mozilla\Firefox\Profiles'),
        'cookies_db': 'cookies.sqlite',
    },
    'edge': {
        'win': os.path.expanduser(r'~\AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies'),
        'cookies_db': 'cookies',
    },
}


def get_browser_cookie_path(browser: str) -> Optional[str]:
    path = BROWSER_PATHS.get(browser.lower(), {}).get('win')
    if path and os.path.exists(path):
        return path
    return None


def get_chrome_cookies() -> Optional[str]:
    chrome_path = os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies')
    if os.path.exists(chrome_path):
        temp_path = os.path.expanduser(r'~\AppData\Local\Temp\vdownloader_cookies.sqlite')
        try:
            conn = sqlite3.connect(chrome_path)
            backup_conn = sqlite3.connect(temp_path)
            conn.backup(backup_conn)
            conn.close()
            backup_conn.close()
            return temp_path
        except Exception:
            return None
    return None


def get_firefox_cookies() -> Optional[str]:
    firefox_base = os.path.expanduser(r'~\AppData\Roaming\Mozilla\Firefox\Profiles')
    if not os.path.exists(firefox_base):
        return None
    
    for profile in os.listdir(firefox_base):
        profile_path = os.path.join(firefox_base, profile)
        if os.path.isdir(profile_path):
            cookies_path = os.path.join(profile_path, 'cookies.sqlite')
            if os.path.exists(cookies_path):
                temp_path = os.path.expanduser(r'~\AppData\Local\Temp\vdownloader_firefox_cookies.sqlite')
                try:
                    conn = sqlite3.connect(cookies_path)
                    backup_conn = sqlite3.connect(temp_path)
                    conn.backup(backup_conn)
                    conn.close()
                    backup_conn.close()
                    return temp_path
                except Exception:
                    return None
    return None


def get_edge_cookies() -> Optional[str]:
    edge_path = os.path.expanduser(r'~\AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies')
    if os.path.exists(edge_path):
        temp_path = os.path.expanduser(r'~\AppData\Local\Temp\vdownloader_edge_cookies.sqlite')
        try:
            conn = sqlite3.connect(edge_path)
            backup_conn = sqlite3.connect(temp_path)
            conn.backup(backup_conn)
            conn.close()
            backup_conn.close()
            return temp_path
        except Exception:
            return None
    return None


class CookieManager:
    BROWSERS = ['chrome', 'firefox', 'edge']
    
    def __init__(self):
        self.config_dir = Path.home() / ".vdownloader"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "cookies_config.json"
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {'preferred_browser': None}
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def auto_detect_browser(self) -> Optional[str]:
        for browser in self.BROWSERS:
            if browser == 'chrome':
                if get_chrome_cookies():
                    return 'chrome'
            elif browser == 'firefox':
                if get_firefox_cookies():
                    return 'firefox'
            elif browser == 'edge':
                if get_edge_cookies():
                    return 'edge'
        return None
    
    def get_cookies(self, browser: Optional[str] = None) -> Optional[str]:
        target_browser = browser or self.config.get('preferred_browser')
        
        if target_browser:
            if target_browser == 'chrome':
                return get_chrome_cookies()
            elif target_browser == 'firefox':
                return get_firefox_cookies()
            elif target_browser == 'edge':
                return get_edge_cookies()
        
        detected = self.auto_detect_browser()
        if detected:
            return self.get_cookies(detected)
        
        return None
    
    def set_preferred_browser(self, browser: str):
        self.config['preferred_browser'] = browser
        self.save_config()
    
    def get_available_browsers(self):
        available = []
        for browser in self.BROWSERS:
            if self.get_cookies(browser):
                available.append(browser)
        return available