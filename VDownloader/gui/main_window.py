import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QProgressBar, QRadioButton,
    QButtonGroup, QComboBox, QFileDialog, QMessageBox, QFrame,
    QCheckBox, QGroupBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer
from PyQt6.QtGui import QIcon, QAction, QFont, QLinearGradient, QColor, QPainter

from core.video_info import VideoInfo
from core.downloader import DownloadThread
from core.ffmpeg_check import FFmpegChecker
from utils.cookies import CookieManager
from utils.proxy import ProxyManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_info = None
        self.download_thread = None
        self.cookie_manager = CookieManager()
        self.proxy_manager =ProxyManager()
        
        self.init_ui()
        self.check_ffmpeg()
        
        self._check_startup_updates()
    
    def _check_startup_updates(self):
        import json
        from pathlib import Path
        
        config_dir = Path.home() / ".vdownloader"
        config_dir.mkdir(exist_ok=True)
        last_check_file = config_dir / "last_update_check"
        
        should_check = True
        if last_check_file.exists():
            try:
                import time
                last_check = float(last_check_file.read_text())
                if time.time() - last_check < 86400:
                    should_check = False
            except:
                pass
        
        if should_check:
            import time
            last_check_file.write_text(str(time.time()))
            from utils.updater import check_for_updates
            QTimer.singleShot(2000, lambda: check_for_updates(self))
    
    def init_ui(self):
        self.setWindowTitle("VDownloader")
        self.setMinimumSize(600, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
            }
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                color: #cdd6f4;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: #1e1e2e;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
            QProgressBar {
                background-color: #313244;
                border-radius: 8px;
                text-align: center;
                color: #cdd6f4;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #89b4fa;
                border-radius: 8px;
            }
            QRadioButton {
                color: #cdd6f4;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox {
                color: #cdd6f4;
            }
            QGroupBox {
                border: 1px solid #45475a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #cdd6f4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 8px;
                color: #cdd6f4;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #cdd6f4;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("VDownloader")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #89b4fa;
            padding-bottom: 10px;
        """)
        main_layout.addWidget(title_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("رابط الفيديو...")
        main_layout.addWidget(self.url_input)
        
        self.analyze_btn = QPushButton("فحص الفيديو")
        self.analyze_btn.clicked.connect(self.analyze_video)
        main_layout.addWidget(self.analyze_btn)
        
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setSpacing(10)
        
        self.title_label = QLabel("العنوان: --")
        info_layout.addWidget(self.title_label)
        
        self.duration_label = QLabel("المدة: --")
        info_layout.addWidget(self.duration_label)
        
        quality_group = QGroupBox("الجودة")
        quality_layout = QVBoxLayout(quality_group)
        
        self.quality_combo = QComboBox()
        self.quality_combo.setStyleSheet("""
            QComboBox {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 12px;
                color: #cdd6f4;
                font-size: 14px;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                border-width: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #313244;
                color: #cdd6f4;
                selection-background-color: #45475a;
                border: 1px solid #45475a;
            }
        """)
        
        quality_layout.addWidget(self.quality_combo)
        
        info_layout.addWidget(quality_group)
        
        main_layout.addWidget(self.info_frame)
        self.info_frame.hide()
        
        save_group = QGroupBox("مجلد الحفظ")
        save_layout = QHBoxLayout(save_group)
        
        self.save_path_input = QLineEdit()
        self.save_path_input.setText(os.path.join(os.path.expanduser("~"), "Downloads"))
        save_layout.addWidget(self.save_path_input, 1)
        
        self.browse_btn = QPushButton("استعراض")
        self.browse_btn.clicked.connect(self.browse_folder)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        save_layout.addWidget(self.browse_btn)
        
        main_layout.addWidget(save_group)
        
        self.download_btn = QPushButton("تحميل")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        main_layout.addWidget(self.download_btn)
        
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        status_layout = QHBoxLayout()
        self.status_label = QLabel("جاهز")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.speed_label = QLabel("")
        status_layout.addWidget(self.speed_label)
        
        main_layout.addLayout(status_layout)
        
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QMenuBar::item:selected {
                background-color: #313244;
            }
            QMenu {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
            }
            QMenu::item:selected {
                background-color: #45475a;
            }
        """)
        
        settings_action = QAction("الإعدادات", self)
        settings_action.triggered.connect(self.open_settings)
        menubar.addAction(settings_action)
        
        update_action = QAction("التحقق من تحديثات", self)
        update_action.triggered.connect(self.check_updates)
        menubar.addAction(update_action)
    
    def check_updates(self):
        from utils.updater import check_for_updates
        check_for_updates(self)
    
    def check_ffmpeg(self):
        available, ffmpeg_path, ffprobe_path = FFmpegChecker.check()
        if not available:
            QMessageBox.warning(
                self,
                "FFmpeg غير موجود",
                "يرجى تثبيت FFmpeg لتحميل الفيديوهات.<br>"
                "تحميل من: <a href='https://ffmpeg.org/download.html'>ffmpeg.org</a>"
            )
    
    def analyze_video(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال رابط الفيديو")
            return
        
        self.status_label.setText("جاري فحص الفيديو...")
        self.analyze_btn.setEnabled(False)
        
        proxy = self.proxy_manager.get_proxy(self.proxy_combo.currentText()) if hasattr(self, 'proxy_combo') else None
        cookies = self.cookie_manager.get_cookies() if hasattr(self, 'cookie_manager') else None
        
        self.worker_thread = QThread()
        self.worker = VideoInfoWorker(url, proxy, cookies)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_analyze_finished)
        self.worker.error.connect(self.on_analyze_error)
        
        self.worker_thread.start()
    
    def on_analyze_finished(self, info):
        self.video_info = info
        self.worker_thread.quit()
        
        self.title_label.setText(f"العنوان: {info.get('title', '')}")
        
        duration = info.get('duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        self.duration_label.setText(f"المدة: {minutes}:{seconds:02d}")
        
        self.quality_combo.clear()
        formats = info.get('formats', [])
        
        quality_options = []
        seen_heights = set()
        
        for f in formats:
            height = f.get('height', 0)
            vcodec = f.get('vcodec', 'none')
            
            if height > 0 and vcodec != 'none' and height not in seen_heights:
                seen_heights.add(height)
                
                if height >= 2160:
                    label = "4K - Ultra HD"
                elif height >= 1080:
                    label = "1080p - Full HD"
                elif height >= 720:
                    label = "720p - HD"
                elif height >= 480:
                    label = "480p - SD"
                else:
                    label = f"{height}p"
                
                fid = f"{height}+bestaudio/best[height>={height}]"
                quality_options.append((label, fid))
        
        quality_options.sort(key=lambda x: int(x[0].split('p')[0]) if x[0][0].isdigit() else 0, reverse=True)
        
        for label, fid in quality_options:
            self.quality_combo.addItem(label, fid)
        
        if self.quality_combo.count() == 0:
            self.quality_combo.addItem("الأفضل متاح", "best")
        
        self.info_frame.show()
        self.download_btn.setEnabled(True)
        self.status_label.setText("تم فحص الفيديو بنجاح")
        self.analyze_btn.setEnabled(True)
    
    def on_analyze_error(self, error):
        self.worker_thread.quit()
        QMessageBox.critical(self, "خطأ", str(error))
        self.status_label.setText("فشل في فحص الفيديو")
        self.analyze_btn.setEnabled(True)
    
    def quality_selected(self, button):
        pass
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد الحفظ")
        if folder:
            self.save_path_input.setText(folder)
    
    def start_download(self):
        if not self.video_info:
            return
        
        if self.quality_combo.currentIndex() < 0:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار الجودة")
            return
        
        selected_label = self.quality_combo.currentText()
        
        if "4K" in selected_label:
            format_id = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
        elif "1080" in selected_label:
            format_id = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif "720" in selected_label:
            format_id = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif "480" in selected_label:
            format_id = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        elif selected_label.endswith("p"):
            h = selected_label.split("p")[0]
            format_id = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]"
        else:
            format_id = "best"
        
        output_path = self.save_path_input.text()
        
        proxy = None
        if hasattr(self, 'proxy_combo') and self.proxy_combo.currentText():
            proxy = self.proxy_manager.get_proxy(self.proxy_combo.currentText())
        
        cookies = self.cookie_manager.get_cookies()
        
        self.download_thread = DownloadThread(
            self.url_input.text(),
            format_id,
            output_path,
            proxy,
            cookies
        )
        
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        
        self.download_thread.start()
        
        self.download_btn.setText("إلغاء")
        self.download_btn.clicked.connect(self.cancel_download)
        self.status_label.setText("جاري التحميل...")
    
    def on_download_progress(self, percent, speed, filename):
        self.progress_bar.setValue(int(percent))
        self.speed_label.setText(f"السرعة: {speed}")
    
    def on_download_finished(self, filepath, title):
        self.progress_bar.setValue(100)
        self.status_label.setText("تم التحميل بنجاح")
        self.download_btn.setText("تحميل")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(True)
        
        QMessageBox.information(
            self,
            "تم التحميل",
            f"تم تحميل الفيديو بنجاح<br>{title}"
        )
    
    def on_download_error(self, error):
        self.progress_bar.setValue(0)
        self.status_label.setText("فشل في التحميل")
        self.download_btn.setText("تحميل")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(True)
        
        QMessageBox.critical(self, "خطأ", str(error))
    
    def cancel_download(self):
        if self.download_thread:
            self.download_thread.cancel()
            self.status_label.setText("تم الإلغاء")
            self.progress_bar.setValue(0)
            self.download_btn.setText("تحميل")
            self.download_btn.clicked.connect(self.start_download)
    
    def open_settings(self):
        from gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.proxy_manager, self.cookie_manager, self)
        dialog.exec()


class VideoInfoWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, url, proxy, cookies):
        super().__init__()
        self.url = url
        self.proxy = proxy
        self.cookies = cookies
    
    def run(self):
        try:
            info = VideoInfo.get_info(self.url, self.proxy, self.cookies)
            self.finished.emit(info)
        except Exception as e:
            self.error.emit(str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())