import os
import sys
import json
import shutil
import requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt


CURRENT_VERSION = "1.0.0"
UPDATE_URL = "https://api.github.com/repos/yourrepo/vdownloader/releases/latest"


class UpdateChecker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
    
    def run(self):
        try:
            self.status.emit("جاري البحث عن تحديثات...")
            self.progress.emit(10)
            
            response = requests.get(UPDATE_URL, timeout=30)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").replace("v", "")
                
                if self._is_newer(latest_version):
                    self.status.emit("تم العثور على تحديث!")
                    self.progress.emit(30)
                    
                    asset = data.get("assets", [])[0]
                    download_url = asset.get("browser_download_url", "")
                    
                    if download_url:
                        self.status.emit("جاري تحميل التحديث...")
                        self._download_update(download_url)
                else:
                    self.finished.emit(False, "لديك أحدث إصدار")
            else:
                self.finished.emit(False, "لا توجد تحديثات")
        except Exception as e:
            self.error.emit(str(e))
    
    def _is_newer(self, latest):
        try:
            current = tuple(map(int, self.current_version.split(".")))
            latest_tuple = tuple(map(int, latest.split(".")))
            return latest_tuple > current
        except:
            return False
    
    def _download_update(self, url):
        temp_dir = Path(os.environ.get("TEMP", "."))
        exe_path = temp_dir / "VDownloader_update.exe"
        
        response = requests.get(url, stream=True, timeout=60)
        total_size = int(response.headers.get("content-length", 0))
        
        downloaded = 0
        with open(exe_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        self.progress.emit(percent)
        
        self.status.emit("جاري تثبيت التحديث...")
        self.progress.emit(100)
        
        current_exe = sys.executable
        if os.path.exists(current_exe):
            backup = current_exe + ".bak"
            if os.path.exists(backup):
                os.remove(backup)
            shutil.move(current_exe, backup)
        
        shutil.move(str(exe_path), current_exe)
        
        self.finished.emit(True, "تم التحديث بنجاح! يرجى إعادة تشغيل التطبيق")


class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("التحقق من التحديثات")
        self.setMinimumSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
            }
            QPushButton {
                background-color: #89b4fa;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: #1e1e2e;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QProgressBar {
                background-color: #313244;
                border-radius: 8px;
                text-align: center;
                color: #cdd6f4;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        self.title_label = QLabel(f"الإصدار الحالي: {CURRENT_VERSION}")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        self.status_label = QLabel("جاري البحث عن تحديثات...")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.check_btn = QPushButton("تحقق الآن")
        self.check_btn.clicked.connect(self.check_updates)
        btn_layout.addWidget(self.check_btn)
        
        self.close_btn = QPushButton("إغلاق")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
    
    def check_updates(self):
        self.check_btn.setEnabled(False)
        self.status_label.setText("جاري الاتصال...")
        
        self.update_worker = UpdateChecker(CURRENT_VERSION)
        self.update_worker.progress.connect(self.on_progress)
        self.update_worker.status.connect(self.on_status)
        self.update_worker.finished.connect(self.on_finished)
        self.update_worker.error.connect(self.on_error)
        self.update_worker.start()
    
    def on_progress(self, value):
        self.progress_bar.setValue(value)
    
    def on_status(self, text):
        self.status_label.setText(text)
    
    def on_finished(self, updated, message):
        self.check_btn.setEnabled(True)
        self.status_label.setText(message)
        
        if updated:
            QMessageBox.information(self, "تحديث", message)
            self.close()
        else:
            QMessageBox.information(self, "تحديث", message)
    
    def on_error(self, error):
        self.check_btn.setEnabled(True)
        self.status_label.setText(f"خطأ: {error}")
        QMessageBox.critical(self, "خطأ", error)


def check_for_updates(parent=None):
    dialog = UpdateDialog(parent)
    dialog.exec()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = UpdateDialog()
    dialog.exec()