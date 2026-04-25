import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QProgressBar, QRadioButton,
    QButtonGroup, QComboBox, QFileDialog, QMessageBox, QFrame,
    QCheckBox, QGroupBox, QScrollArea, QSizePolicy, QStackedWidget,
    QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer
from PyQt6.QtGui import (
    QIcon, QAction, QFont, QLinearGradient, QColor, QPainter,
    QPalette, QBrush
)

from core.video_info import VideoInfo
from core.downloader import DownloadThread
from core.ffmpeg_check import FFmpegChecker
from utils.cookies import CookieManager
from utils.proxy import ProxyManager


COLORS = {
    'background': '#0D0D0D',
    'card': '#1A1A2E',
    'primary': '#6C63FF',
    'accent': '#00D9FF',
    'success': '#00C853',
    'error': '#FF5252',
    'text': '#FFFFFF',
    'text_secondary': '#A0A0A0',
    'border': '#2D2D44',
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_info = None
        self.download_thread = None
        self.cookie_manager = CookieManager()
        self.proxy_manager = ProxyManager()
        self.selected_format = "best"
        
        self.init_ui()
        self.check_ffmpeg()
        
        self._check_startup_updates()
    
    def _check_startup_updates(self):
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
        self.setMinimumSize(500, 650)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QLineEdit {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['primary']};
            }}
            QLineEdit:placeholder {{
                color: {COLORS['text_secondary']};
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #7C73FF;
            }}
            QPushButton:pressed {{
                background-color: #5C53EF;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_secondary']};
            }}
            QProgressBar {{
                background-color: {COLORS['card']};
                border-radius: 8px;
                text-align: center;
                color: {COLORS['text']};
                border: none;
                height: 12px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 8px;
            }}
            QRadioButton {{
                color: {COLORS['text']};
                padding: 5px;
            }}
            QCheckBox {{
                color: {COLORS['text']};
            }}
            QGroupBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        title_layout = QHBoxLayout()
        title_label = QLabel("⬡ VDownloader ⬡")
        title_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        title_layout.addStretch()
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        url_layout = QHBoxLayout()
        url_layout.setSpacing(8)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("أدخل رابط الفيديو...")
        url_layout.addWidget(self.url_input, 1)
        
        self.paste_btn = QPushButton("📋")
        self.paste_btn.setFixedWidth(45)
        self.paste_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        self.paste_btn.clicked.connect(self.paste_url)
        url_layout.addWidget(self.paste_btn)
        
        main_layout.addLayout(url_layout)
        
        self.analyze_btn = QPushButton("🔄 فحص الفيديو")
        self.analyze_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        self.analyze_btn.clicked.connect(self.analyze_video)
        main_layout.addWidget(self.analyze_btn)
        
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setSpacing(10)
        
        self.title_label = QLabel("العنوان: --")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.title_label)
        
        details_layout = QHBoxLayout()
        
        self.duration_label = QLabel("المدة: --")
        self.duration_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        details_layout.addWidget(self.duration_label)
        
        self.size_label = QLabel("الحجم: --")
        self.size_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        details_layout.addWidget(self.size_label)
        
        self.format_label = QLabel("الصيغة: --")
        self.format_label.setStyleSheet(f"color: {COLORS['accent']};")
        details_layout.addWidget(self.format_label)
        
        details_layout.addStretch()
        info_layout.addLayout(details_layout)
        
        main_layout.addWidget(self.info_frame)
        self.info_frame.hide()
        
        quality_label = QLabel("الجودة:")
        quality_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        main_layout.addWidget(quality_label)
        
        self.quality_scroll = QScrollArea()
        self.quality_scroll.setFixedHeight(45)
        self.quality_scroll.setStyleSheet("border: none;")
        
        self.quality_widget = QWidget()
        self.quality_layout = QHBoxLayout(self.quality_widget)
        self.quality_layout.setSpacing(8)
        self.quality_layout.setContentsMargins(0, 0, 0, 0)
        
        self.quality_scroll.setWidget(self.quality_widget)
        self.quality_scroll.setWidgetResizable(True)
        self.quality_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_layout.addWidget(self.quality_scroll)
        
        self.progress_frame = QFrame()
        self.progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        progress_layout = QVBoxLayout(self.progress_frame)
        progress_layout.setSpacing(8)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        progress_info_layout = QHBoxLayout()
        
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
        progress_info_layout.addWidget(self.percent_label)
        
        self.speed_label = QLabel("")
        self.speed_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        progress_info_layout.addWidget(self.speed_label)
        
        progress_info_layout.addStretch()
        
        self.time_label = QLabel("")
        self.time_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        progress_info_layout.addWidget(self.time_label)
        
        progress_layout.addLayout(progress_info_layout)
        
        main_layout.addWidget(self.progress_frame)
        self.progress_frame.hide()
        
        download_layout = QHBoxLayout()
        download_layout.setSpacing(12)
        
        self.download_btn = QPushButton("▶ تحميل")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.start_download)
        download_layout.addWidget(self.download_btn, 1)
        
        self.folder_btn = QPushButton("📁")
        self.folder_btn.setFixedWidth(50)
        self.folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        self.folder_btn.clicked.connect(self.browse_folder)
        download_layout.addWidget(self.folder_btn)
        
        main_layout.addLayout(download_layout)
        
        self.status_label = QLabel("جاهز للتحميل")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(20)
        
        self.home_btn = QPushButton("🏠")
        self.home_btn.setFixedWidth(50)
        self.home_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text']};
                border-radius: 25px;
            }}
        """)
        nav_layout.addWidget(self.home_btn)
        
        self.history_btn = QPushButton("📥")
        self.history_btn.setFixedWidth(50)
        self.history_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text_secondary']};
                border-radius: 25px;
            }}
        """)
        self.history_btn.clicked.connect(self.go_history)
        nav_layout.addWidget(self.history_btn)
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedWidth(50)
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['card']};
                color: {COLORS['text_secondary']};
                border-radius: 25px;
            }}
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        nav_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(nav_layout)
        
        self.create_menu_bar()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QMenuBar::item:selected {{
                background-color: {COLORS['card']};
            }}
            QMenu {{
                background-color: {COLORS['card']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
            }}
            QMenu::item:selected {{
                background-color: {COLORS['border']};
            }}
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
            msg = QMessageBox.warning(
                self,
                "FFmpeg غير موجود",
                "يرجى تثبيت FFmpeg لتحميل الفيديوهات.<br>"
                "تحميل من: <a href='https://ffmpeg.org/download.html'>ffmpeg.org</a>"
            )
            msg.setTextFormat(Qt.TextFormat.RichText)
    
    def paste_url(self):
        from PyQt6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        url = clipboard.text()
        if url:
            self.url_input.setText(url)
    
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
        
        self.title_label.setText(info.get('title', 'غير معروف')[:60])
        
        duration = info.get('duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        self.duration_label.setText(f"المدة: {minutes}:{seconds:02d}")
        
        filesize = info.get('filesize', 0)
        if filesize > 1024 * 1024 * 1024:
            self.size_label.setText(f"الحجم: {filesize / (1024**3):.1f} GB")
        elif filesize > 1024 * 1024:
            self.size_label.setText(f"الحجم: {filesize / (1024**2):.1f} MB")
        elif filesize > 1024:
            self.size_label.setText(f"الحجم: {filesize / 1024:.1f} KB")
        else:
            self.size_label.setText("الحجم: --")
        
        self.format_label.setText(f"الصيغة: {info.get('ext', 'mp4')}")
        
        self._build_quality_buttons(info.get('formats', []))
        
        self.info_frame.show()
        self.download_btn.setEnabled(True)
        self.status_label.setText("اختر الجودة ثم اضغط تحميل")
        self.download_btn.setText("▶ تحميل")
        self.analyze_btn.setEnabled(True)
    
    def _build_quality_buttons(self, formats):
        for i in reversed(range(self.quality_layout.count())):
            widget = self.quality_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        seen = set()
        quality_map = {}
        button_colors = [COLORS['primary'], COLORS['accent'], COLORS['success'], '#FF9800', COLORS['error']]
        
        for idx, f in enumerate(formats):
            format_id = f.get('format_id', '')
            ext = f.get('ext', '')
            height = f.get('height', 0)
            filesize = f.get('filesize', 0)
            
            if format_id in seen:
                continue
            seen.add(format_id)
            
            if height > 0:
                if height >= 2160:
                    label = "4K"
                elif height >= 1080:
                    label = "FHD"
                elif height >= 720:
                    label = "HD"
                elif height >= 480:
                    label = "SD"
                elif height >= 360:
                    label = "360p"
                else:
                    label = f"{height}p"
            elif ext == 'mp3' or ext == 'm4a':
                label = "Mp3"
            else:
                label = ext.upper()
            
            if filesize > 0:
                if filesize > 1024 * 1024 * 1024:
                    size_str = f"{filesize / (1024**3):.1f}G"
                elif filesize > 1024 * 1024:
                    size_str = f"{filesize / (1024**2):.1f}M"
                else:
                    size_str = f"{filesize / 1024:.0f}K"
                label += f" ({size_str})"
            
            quality_map[label] = format_id
        
        quality_items = list(quality_map.items())[:5]
        
        for idx, (label, format_id) in enumerate(quality_items):
            btn = QPushButton(label)
            btn.setFixedWidth(80)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            color = button_colors[idx % len(button_colors)]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {COLORS['text']};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            
            btn.format_id = format_id
            btn.clicked=lambda clicked, fid=format_id, lbl=label: self._select_quality(fid, lbl)
            
            if idx == 0:
                self.selected_format = format_id
                self.selected_label = label
            
            self.quality_layout.addWidget(btn)
        
        if not quality_map:
            btn = QPushButton("الأفضل")
            btn.setFixedWidth(80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: {COLORS['text']};
                    border: none;
                    border-radius: 8px;
                }}
            """)
            btn.format_id = "best"
            btn.clicked=lambda clicked, fid="best", lbl="الأفضل": self._select_quality(fid, lbl)
            self.quality_layout.addWidget(btn)
            self.selected_format = "best"
    
    def _select_quality(self, format_id, label):
        self.selected_format = format_id
        self.selected_label = label
        
        for i in range(self.quality_layout.count()):
            widget = self.quality_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'format_id'):
                if widget.format_id == format_id:
                    widget.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS['primary']};
                            color: {COLORS['text']};
                            border: 2px solid {COLORS['accent']};
                            border-radius: 8px;
                            padding: 8px 12px;
                            font-size: 12px;
                        }}
                    """)
                else:
                    widget.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS['card']};
                            color: {COLORS['text_secondary']};
                            border: 1px solid {COLORS['border']};
                            border-radius: 8px;
                            padding: 8px 12px;
                            font-size: 12px;
                        }}
                    """)
    
    def on_analyze_error(self, error):
        self.worker_thread.quit()
        QMessageBox.critical(self, "خطأ", str(error))
        self.status_label.setText(f"خطأ: {error}")
        self.analyze_btn.setEnabled(True)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "اختر مجلد الحفظ")
        if folder:
            self.save_path = folder
    
    def start_download(self):
        if not self.video_info:
            return
        
        format_id = self.selected_format or "best"
        output_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
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
        
        self.download_btn.setText("⏹ إيقاف")
        self.download_btn.clicked.disconnect()
        self.download_btn.clicked.connect(self.cancel_download)
        self.status_label.setText("جاري التحميل...")
        
        self.progress_frame.show()
    
    def on_download_progress(self, percent, speed, filename):
        self.progress_bar.setValue(int(percent))
        self.percent_label.setText(f"{int(percent)}%")
        self.speed_label.setText(speed)
        self.status_label.setText(f"جاري التحميل... {int(percent)}%")
    
    def on_download_finished(self, filepath, title):
        self.progress_bar.setValue(100)
        self.percent_label.setText("100%")
        self.status_label.setText("تم التحميل بنجاح!")
        self.download_btn.setText("▶ تحميل")
        self.download_btn.clicked.disconnect()
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(True)
        
        self.progress_frame.hide()
        
        QMessageBox.information(
            self,
            "تم التحميل",
            f"تم تحميل الفيديو بنجاح\n{title}"
        )
    
    def on_download_error(self, error):
        self.status_label.setText(f"خطأ: {error}")
        self.download_btn.setText("▶ تحميل")
        self.download_btn.clicked.disconnect()
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(True)
        
        self.progress_frame.hide()
        
        QMessageBox.critical(self, "خطأ", str(error))
    
    def cancel_download(self):
        if self.download_thread:
            self.download_thread.cancel()
            self.status_label.setText("تم الإلغاء")
            self.progress_bar.setValue(0)
            self.download_btn.setText("▶ تحميل")
            self.download_btn.clicked.disconnect()
            self.download_btn.clicked.connect(self.start_download)
            self.download_btn.setEnabled(True)
            self.progress_frame.hide()
    
    def go_history(self):
        from gui.history_dialog import HistoryDialog
        dialog = HistoryDialog(self)
        dialog.exec()
    
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
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['background']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS['text']))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())