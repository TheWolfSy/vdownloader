import os
import sys
import json
import shutil
import requests
import platform
import threading
from pathlib import Path


CURRENT_VERSION = "1.0.0"
UPDATE_URL = "https://api.github.com/repos/yourrepo/vdownloader/releases/latest"


class UpdateChecker:
    def __init__(self, current_version, on_progress=None, on_status=None, on_finished=None, on_error=None):
        self.current_version = current_version
        self.on_progress = on_progress
        self.on_status = on_status
        self.on_finished = on_finished
        self.on_error = on_error

    def check(self):
        thread = threading.Thread(target=self._check_worker)
        thread.daemon = True
        thread.start()

    def _check_worker(self):
        try:
            if self.on_status:
                self.on_status("جاري البحث عن تحديثات...")
            if self.on_progress:
                self.on_progress(10)

            response = requests.get(UPDATE_URL, timeout=30)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").replace("v", "")

                if self._is_newer(latest_version):
                    if self.on_status:
                        self.on_status("تم العثور على تحديث!")
                    if self.on_progress:
                        self.on_progress(30)

                    asset = data.get("assets", [])[0]
                    download_url = asset.get("browser_download_url", "")

                    if download_url:
                        self._download_update(download_url)
                else:
                    if self.on_finished:
                        self.on_finished(False, "لديك أحدث إصدار")
            else:
                if self.on_finished:
                    self.on_finished(False, "لا توجد تحديثات")
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))

    def _is_newer(self, latest):
        try:
            current = tuple(map(int, self.current_version.split(".")))
            latest_tuple = tuple(map(int, latest.split(".")))
            return latest_tuple > current
        except:
            return False

    def _download_update(self, url):
        temp_dir = Path(os.environ.get("TEMP", "."))
        is_android = platform.system() == "Linux" and "ANDROID" in os.environ

        if is_android:
            download_path = temp_dir / "VDownloader.apk"
        else:
            download_path = temp_dir / "VDownloader_update.exe"

        if self.on_status:
            self.on_status("جاري تحميل التحديث...")
        if self.on_progress:
            self.on_progress(40)

        response = requests.get(url, stream=True, timeout=60)
        total_size = int(response.headers.get("content-length", 0))

        downloaded = 0
        with open(download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = 40 + int((downloaded / total_size) * 50)
                        if self.on_progress:
                            self.on_progress(percent)

        if self.on_status:
            self.on_status("جاري تثبيت التحديث...")
        if self.on_progress:
            self.on_progress(95)

        if is_android:
            self._install_android_apk(download_path)
        else:
            self._install_desktop_exe(download_path)

    def _install_desktop_exe(self, exe_path):
        current_exe = sys.executable
        if os.path.exists(current_exe):
            backup = current_exe + ".bak"
            if os.path.exists(backup):
                os.remove(backup)
            shutil.move(current_exe, backup)

        shutil.move(str(exe_path), current_exe)

        if self.on_progress:
            self.on_progress(100)
        if self.on_finished:
            self.on_finished(True, "تم التحديث بنجاح! يرجى إعادة تشغيل التطبيق")

    def _install_android_apk(self, apk_path):
        try:
            from jnius import autoclass
            from android import python_act

            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            FileProvider = autoclass('androidx.core.content.FileProvider')

            content_uri = FileProvider.getUriForFile(
                python_act,
                "org.vdownloader.fileprovider",
                apk_path
            )

            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(content_uri, "application/vnd.android.package-archive")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

            python_act.startActivity(intent)

            if self.on_progress:
                self.on_progress(100)
            if self.on_finished:
                self.on_finished(True, "تم تحميل التحديث! سيتم تثبييت بعد التثبيت")
        except Exception as e:
            if self.on_error:
                self.on_error(str(e))


def check_for_updates(parent=None, on_progress=None, on_status=None, on_finished=None, on_error=None):
    checker = UpdateChecker(
        CURRENT_VERSION,
        on_progress=on_progress,
        on_status=on_status,
        on_finished=on_finished,
        on_error=on_error
    )
    checker.check()


def check_for_updates_sync():
    try:
        response = requests.get(UPDATE_URL, timeout=30)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("tag_name", "").replace("v", "")

            current = tuple(map(int, CURRENT_VERSION.split(".")))
            latest = tuple(map(int, latest_version.split(".")))

            if latest > current:
                return True, latest_version
        return False, CURRENT_VERSION
    except:
        return False, CURRENT_VERSION


if __name__ == "__main__":
    check_for_updates(
        on_progress=lambda p: print(f"Progress: {p}%"),
        on_status=lambda s: print(f"Status: {s}"),
        on_finished=lambda u, m: print(f"Finished: {u}, {m}"),
        on_error=lambda e: print(f"Error: {e}")
    )