import os
import json
import shutil
import platform
from pathlib import Path
from typing import Optional


BROWSER_PATHS = {
    'chrome': {
        'win': os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies'),
        'linux': os.path.expanduser(r'~/.config/google-chrome/Default/Cookies'),
        'android': '/data/data/com.android.chrome/app_chrome/Default/Cookies',
    },
    'firefox': {
        'win': os.path.expanduser(r'~\AppData\Roaming\Mozilla\Firefox\Profiles'),
        'linux': os.path.expanduser(r'~/.mozilla/firefox'),
        'android': '/data/data/org.mozilla.firefox/files/mozilla',
    },
    'edge': {
        'win': os.path.expanduser(r'~\AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies'),
        'linux': os.path.expanduser(r'~/.config/microsoft-edge/Default/Cookies'),
        'android': '/data/data/com.microsoft.emmx/app_edge_default/WebView2/Default/Cookies',
    },
}


def get_cookie_path(browser: str) -> Optional[str]:
    system = platform.system().lower()
    if system == 'windows':
        system = 'win'
    elif system == 'linux' and 'ANDROID' not in os.environ:
        system = 'linux'
    else:
        system = 'android'

    path = BROWSER_PATHS.get(browser.lower(), {}).get(system)
    if path and os.path.exists(path):
        return path
    return None


def get_chrome_cookies() -> Optional[str]:
    path = get_cookie_path('chrome')
    if not path:
        return None

    if platform.system() == 'windows':
        return _copy_windows_cookies(path, 'chrome')
    return path


def get_firefox_cookies() -> Optional[str]:
    path = get_cookie_path('firefox')
    if not path:
        return None

    if platform.system() == 'windows' and os.path.isdir(path):
        for profile in os.listdir(path):
            profile_path = os.path.join(path, profile)
            if os.path.isdir(profile_path):
                cookies_path = os.path.join(profile_path, 'cookies.sqlite')
                if os.path.exists(cookies_path):
                    return _copy_windows_cookies(cookies_path, 'firefox')
    return path


def get_edge_cookies() -> Optional[str]:
    path = get_cookie_path('edge')
    if not path:
        return None

    if platform.system() == 'windows':
        return _copy_windows_cookies(path, 'edge')
    return path


def _copy_windows_cookies(source_path: str, browser: str) -> Optional[str]:
    temp_dir = os.environ.get("TEMP", os.path.expanduser("~"))
    temp_path = os.path.join(temp_dir, f"vdownloader_{browser}_cookies.sqlite")
    try:
        from shutil import copy2
        copy2(source_path, temp_path)
        return temp_path
    except Exception:
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
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {'preferred_browser': None}
        else:
            self.config = {'preferred_browser': None}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def auto_detect_browser(self) -> Optional[str]:
        for browser in self.BROWSERS:
            path = get_cookie_path(browser)
            if path:
                return browser
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
            path = get_cookie_path(browser)
            if path:
                available.append(browser)
        return available

    def is_android(self) -> bool:
        return platform.system() == 'Linux' and 'ANDROID' in os.environ


if __name__ == "__main__":
    cm = CookieManager()
    print(f"Available browsers: {cm.get_available_browsers()}")
    print(f"Is Android: {cm.is_android()}")