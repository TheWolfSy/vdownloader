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
    'background': '#0A0A0A',
    'surface': '#141414',
    'surface_elevated': '#1F1F1F',
    'primary': '#FFFFFF',
    'primary_dim': '#B3B3B3',
    'accent': '#E0E0E0',
    'text': '#FAFAFA',
    'text_secondary': '#808080',
    'border': '#2A2A2A',
    'success': '#4ADE80',
    'error': '#F87171',
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
        self.setMinimumSize(420, 560)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QLineEdit {{
                background-color: {COLORS['surface']};
                border: none;
                border-radius: 8px;
                padding: 14px;
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                background-color: {COLORS['surface_elevated']};
            }}
            QLineEdit:placeholder {{
                color: {COLORS['text_secondary']};
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                border: none;
                border-radius: 8px;
                padding: 14px 20px;
                color: {COLORS['background']};
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dim']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['surface_elevated']};
                color: {COLORS['text_secondary']};
            }}
            QProgressBar {{
                background-color: {COLORS['surface_elevated']};
                border-radius: 4px;
                text-align: center;
                color: {COLORS['text']};
                border: none;
                height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
                border-radius: 4px;
            }}
            QGroupBox {{
                border: none;
                margin-top: 10px;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 0px;
                padding: 0;
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        
        title_label = QLabel("V")
        title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        title_layout.addWidget(title_label)
        
        downloader_label = QLabel("DOWNLOADER")
        downloader_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 4px;
            color: {COLORS['primary']};
        """)
        title_layout.addWidget(downloader_label)
        
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        url_layout = QHBoxLayout()
        url_layout.setSpacing(10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste video URL")
        url_layout.addWidget(self.url_input, 1)
        
        self.paste_btn = QPushButton("📋")
        self.paste_btn.setFixedWidth(45)
        self.paste_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_secondary']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_elevated']};
            }}
        """)
        self.paste_btn.clicked.connect(self.paste_url)
        url_layout.addWidget(self.paste_btn)
        
        main_layout.addLayout(url_layout)
        
        self.analyze_btn = QPushButton("↻ Analyze")
        self.analyze_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                color: {COLORS['primary']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['surface_elevated']};
            }}
        """)
        self.analyze_btn.clicked.connect(self.analyze_video)
        main_layout.addWidget(self.analyze_btn)
        
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setSpacing(8)
        
        self.title_label = QLabel("Title")
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.title_label)
        
        details_layout = QHBoxLayout()
        
        self.duration_label = QLabel("--:--")
        self.duration_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        details_layout.addWidget(self.duration_label)
        
        self.size_label = QLabel("--")
        self.size_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        details_layout.addWidget(self.size_label)
        
        details_layout.addStretch()
        info_layout.addLayout(details_layout)
        
        main_layout.addWidget(self.info_frame)
        self.info_frame.hide()
        
        quality_label = QLabel("Quality")
        quality_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        main_layout.addWidget(quality_label)
        
        self.quality_scroll = QScrollArea()
        self.quality_scroll.setFixedHeight(40)
        self.quality_scroll.setStyleSheet("border: none; background: transparent;")
        
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
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 16px;
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
        progress_layout.addLayout(progress_info_layout)
        
        main_layout.addWidget(self.progress_frame)
        self.progress_frame.hide()
        
        self.download_btn = QPushButton("↓ Download")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_btn)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(24)
        
        self.home_btn = QPushButton("⬤")
        self.home_btn.setFixedWidth(40)
        self.home_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['background']};
                border-radius: 20px;
            }}
        """)
        nav_layout.addWidget(self.home_btn)
        
        self.history_btn = QPushButton("⬤")
        self.history_btn.setFixedWidth(40)
        self.history_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface_elevated']};
                color: {COLORS['surface_elevated']};
                border-radius: 20px;
            }}
        """)
        self.history_btn.clicked.connect(self.go_history)
        nav_layout.addWidget(self.history_btn)
        
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedWidth(40)
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface_elevated']};
                color: {COLORS['text_secondary']};
                border-radius: 20px;
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
                background-color: {COLORS['surface']};
            }}
            QMenu {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
            }}
            QMenu::item:selected {{
                background-color: {COLORS['surface_elevated']};
            }}
        """)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        menubar.addAction(settings_action)
    
    def check_updates(self):
        from utils.updater import check_for_updates
        check_for_updates(self)
    
    def check_ffmpeg(self):
        available, ffmpeg_path, ffprobe_path = FFmpegChecker.check()
        if not available:
            msg = QMessageBox.warning(
                self,
                "FFmpeg Missing",
                "FFmpeg is required for video downloading.<br>"
                "Download from: <a href='https://ffmpeg.org/download.html'>ffmpeg.org</a>"
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
            QMessageBox.warning(self, "Error", "Please enter a video URL")
            return
        
        self.status_label.setText("Analyzing...")
        self.analyze_btn.setEnabled(False)
        
        self.worker_thread = QThread()
        self.worker = VideoInfoWorker(url, None, None)
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_analyze_finished)
        self.worker.error.connect(self.on_analyze_error)
        
        self.worker_thread.start()
    
    def on_analyze_finished(self, info):
        self.video_info = info
        self.worker_thread.quit()
        
        self.title_label.setText(info.get('title', 'Unknown')[:60])
        
        duration = info.get('duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        self.duration_label.setText(f"{minutes}:{seconds:02d}")
        
        filesize = info.get('filesize', 0)
        if filesize > 1024 * 1024 * 1024:
            self.size_label.setText(f"{filesize / (1024**3):.1f} GB")
        elif filesize > 1024 * 1024:
            self.size_label.setText(f"{filesize / (1024**2):.1f} MB")
        else:
            self.size_label.setText(f"{filesize / 1024:.0f} KB")
        
        self._build_quality_buttons(info.get('formats', [])[:5])
        
        self.info_frame.show()
        self.download_btn.setEnabled(True)
        self.status_label.text = "Select quality & download"
        self.download_btn.setText("↓ Download")
        self.analyze_btn.setEnabled(True)
    
    def _build_quality_buttons(self, formats):
        for i in reversed(range(self.quality_layout.count())):
            widget = self.quality_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        seen = set()
        quality_map = {}
        
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
                    label = "1080p"
                elif height >= 720:
                    label = "720p"
                elif height >= 480:
                    label = "480p"
                else:
                    label = f"{height}p"
            elif ext == 'mp3' or ext == 'm4a':
                label = "MP3"
            else:
                label = ext.upper()
            
            quality_map[label] = format_id
        
        quality_items = list(quality_map.items())[:5]
        button_colors = [COLORS['primary'], COLORS['surface_elevated'], COLORS['surface_elevated'], COLORS['surface_elevated'], COLORS['surface_elevated']]
        
        for idx, (label, format_id) in enumerate(quality_items):
            btn = QPushButton(label)
            btn.setFixedWidth(70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            color = button_colors[idx]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {'#0A0A0A' if idx == 0 else '#808080'};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: {'bold' if idx == 0 else 'normal'};
                }}
            """)
            
            btn.format_id = format_id
            btn.clicked=lambda clicked, fid=format_id, lbl=label: self._select_quality(fid, lbl)
            
            if idx == 0:
                self.selected_format = format_id
            
            self.quality_layout.addWidget(btn)
        
        if not quality_map:
            btn = QPushButton("Auto")
            btn.setFixedWidth(70)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: {COLORS['background']};
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }}
            """)
            btn.format_id = "best"
            btn.clicked=lambda clicked, fid="best", lbl="Auto": self._select_quality(fid, lbl)
            self.quality_layout.addWidget(btn)
            self.selected_format = "best"
    
    def _select_quality(self, format_id, label):
        self.selected_format = format_id
        
        for i in range(self.quality_layout.count()):
            widget = self.quality_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'format_id'):
                if widget.format_id == format_id:
                    widget.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS['primary']};
                            color: {COLORS['background']};
                            border: none;
                            border-radius: 8px;
                            padding: 8px 12px;
                            font-size: 12px;
                            font-weight: bold;
                        }}
                    """)
                else:
                    widget.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {COLORS['surface_elevated']};
                            color: {COLORS['text_secondary']};
                            border: none;
                            border-radius: 8px;
                            padding: 8px 12px;
                            font-size: 12px;
                        }}
                    """)
    
    def on_analyze_error(self, error):
        self.worker_thread.quit()
        QMessageBox.critical(self, "Error", str(error))
        self.status_label.setText(f"Error: {error}")
        self.analyze_btn.setEnabled(True)
    
    def start_download(self):
        if not self.video_info:
            return
        
        format_id = self.selected_format or "best"
        output_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        cookies = self.cookie_manager.get_cookies()
        
        self.download_thread = DownloadThread(
            self.url_input.text(),
            format_id,
            output_path,
            None,
            cookies
        )
        
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        
        self.download_thread.start()
        
        self.download_btn.setText("■ Stop")
        self.download_btn.clicked.disconnect()
        self.download_btn.clicked.connect(self.cancel_download)
        self.status_label.text = "Downloading..."
        
        self.progress_frame.show()
    
    def on_download_progress(self, percent, speed, filename):
        self.progress_bar.setValue(int(percent))
        self.percent_label.setText(f"{int(percent)}%")
        self.speed_label.setText(speed)
        self.status_label.setText(f"Downloading {int(percent)}%")
    
    def on_download_finished(self, filepath, title):
        self.progress_bar.setValue(100)
        self.status_label.setText("Download complete")
        self.download_btn.setText("↓ Download")
        self.download_btn.clicked.disconnect()
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(True)
        
        self.progress_frame.hide()
        
        QMessageBox.information(self, "Complete", f"Downloaded: {title}")
    
    def on_download_error(self, error):
        self.status_label.setText(f"Error: {error}")
        self.download_btn.setText("↓ Download")
        self.download_btn.clicked.disconnect()
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(True)
        
        self.progress_frame.hide()
        
        QMessageBox.critical(self, "Error", str(error))
    
    def cancel_download(self):
        if self.download_thread:
            self.download_thread.cancel()
            self.status_label.setText("Cancelled")
            self.progress_bar.setValue(0)
            self.download_btn.setText("↓ Download")
            self.download_btn.clicked.disconnect()
            self.download_btn.clicked.connect(self.start_download)
            self.download_btn.setEnabled(True)
            self.progress_frame.hide()
    
    def go_history(self):
        pass
    
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