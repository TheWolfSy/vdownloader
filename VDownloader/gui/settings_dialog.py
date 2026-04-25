from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QListWidget, QCheckBox, QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, proxy_manager, cookie_manager, parent=None):
        super().__init__(parent)
        self.proxy_manager = proxy_manager
        self.cookie_manager = cookie_manager
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("الإعدادات")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
                padding: 5px;
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
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QComboBox {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 8px;
                color: #cdd6f4;
            }
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                color: #cdd6f4;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QListWidget {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                color: #cdd6f4;
            }
            QCheckBox {
                color: #cdd6f4;
                padding: 5px;
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
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        proxy_group = QGroupBox("إعدادات البروكسي")
        proxy_layout = QVBoxLayout(proxy_group)
        
        proxy_select_layout = QHBoxLayout()
        proxy_select_layout.addWidget(QLabel("اختر البروكسي:"))
        
        self.proxy_combo = QComboBox()
        self.proxy_combo.addItem("-- لا يوجد --", "")
        for name, url in self.proxy_manager.get_all_proxies():
            self.proxy_combo.addItem(f"{name} ({url})", url)
        proxy_select_layout.addWidget(self.proxy_combo, 1)
        proxy_layout.addLayout(proxy_select_layout)
        
        proxy_add_layout = QHBoxLayout()
        proxy_add_layout.addWidget(QLabel("اسم البروكسي:"))
        
        self.proxy_name_input = QLineEdit()
        self.proxy_name_input.setPlaceholderText("اسم البروكسي")
        proxy_add_layout.addWidget(self.proxy_name_input)
        proxy_layout.addLayout(proxy_add_layout)
        
        proxy_url_layout = QHBoxLayout()
        proxy_url_layout.addWidget(QLabel("رابط البروكسي:"))
        
        self.proxy_url_input = QLineEdit()
        self.proxy_url_input.setPlaceholderText("http://ip:port")
        proxy_url_layout.addWidget(self.proxy_url_input)
        proxy_layout.addLayout(proxy_url_layout)
        
        self.add_proxy_btn = QPushButton("إضافة")
        self.add_proxy_btn.clicked.connect(self.add_proxy)
        proxy_layout.addWidget(self.add_proxy_btn)
        
        self.remove_proxy_btn = QPushButton("حذف المحدد")
        self.remove_proxy_btn.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #1e1e2e;
            }
            QPushButton:hover {
                background-color: #eb6f8c;
            }
        """)
        self.remove_proxy_btn.clicked.connect(self.remove_proxy)
        proxy_layout.addWidget(self.remove_proxy_btn)
        
        layout.addWidget(proxy_group)
        
        cookies_group = QGroupBox("إعدادات الكوكيز")
        cookies_layout = QVBoxLayout(cookies_group)
        
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("المتصفح:"))
        
        self.browser_combo = QComboBox()
        available_browsers = self.cookie_manager.get_available_browsers()
        if not available_browsers:
            available_browsers = ['chrome', 'firefox', 'edge']
        
        self.browser_combo.addItem("اكتشاف تلقائي", "auto")
        for browser in available_browsers:
            self.browser_combo.addItem(browser.capitalize(), browser)
        
        browser_layout.addWidget(self.browser_combo, 1)
        cookies_layout.addLayout(browser_layout)
        
        self.cookies_status = QLabel("الكوكيز: غير متوفرة")
        cookies_layout.addWidget(self.cookies_status)
        
        layout.addWidget(cookies_group)
        
        virus_group = QGroupBox("فحص VirusTotal (اختياري)")
        virus_layout = QVBoxLayout(virus_group)
        
        self.virus_scan_check = QCheckBox("فحص الروابط قبل التحميل")
        virus_layout.addWidget(self.virus_scan_check)
        
        layout.addWidget(virus_group)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_btn = QPushButton("حفظ")
        self.save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def add_proxy(self):
        name = self.proxy_name_input.text().strip()
        url = self.proxy_url_input.text().strip()
        
        if not name or not url:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم ورابط البروكسي")
            return
        
        self.proxy_manager.add_proxy(name, url)
        
        self.proxy_combo.addItem(f"{name} ({url})", url)
        
        self.proxy_name_input.clear()
        self.proxy_url_input.clear()
        
        QMessageBox.information(self, "نجاح", "تمت إضافة البروكسي بنجاح")
    
    def remove_proxy(self):
        current_index = self.proxy_combo.currentIndex()
        if current_index <= 0:
            return
        
        current_text = self.proxy_combo.currentText()
        name = current_text.split(" (")[0]
        
        self.proxy_manager.remove_proxy(name)
        self.proxy_combo.removeItem(current_index)
        
        QMessageBox.information(self, "نجاح", "تم حذف البروكسي بنجاح")
    
    def save_settings(self):
        browser = self.browser_combo.currentData()
        if browser != "auto":
            self.cookie_manager.set_preferred_browser(browser)
        
        self.accept()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    from utils.proxy import ProxyManager
    from utils.cookies import CookieManager
    
    proxy_manager = ProxyManager()
    cookie_manager = CookieManager()
    
    dialog = SettingsDialog(proxy_manager, cookie_manager)
    dialog.exec()