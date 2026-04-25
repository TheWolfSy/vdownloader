import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.clock import Clock

from core.video_info import VideoInfo
from core.downloader import Downloader
from utils.proxy import ProxyManager
from utils.cookies import CookieManager
from utils.notifications import show_download_complete, show_download_error


KV = """
<VDownloaderGUI>:
    orientation: 'vertical'
    padding: 20
    spacing: 15

    Label:
        text: 'VDownloader'
        font_size: '28sp'
        bold: True
        color: 0.537, 0.706, 0.980, 1
        size_hint_y: None
        height: 50

    TextInput:
        id: url_input
        hint_text: 'رابط الفيديو...'
        multiline: False
        size_hint_y: None
        height: 50

    Button:
        id: analyze_btn
        text: 'فحص الفيديو'
        on_press: root.analyze_video()
        background_color: 0.537, 0.706, 0.980, 1
        color: 0.118, 0.118, 0.180, 1

    Frame:
        id: info_frame
        opacity: 0 if root.info_hidden else 1
        disabled: root.info_hidden

    Label:
        id: title_label
        text: 'العنوان: --'
        text_size: self.width, None
        size_hint_y: None
        height: 30

    Label:
        id: duration_label
        text: 'المدة: --'
        size_hint_y: None
        height: 30

    Spinner:
        id: quality_spinner
        text: 'اختر الجودة'
        values: root.quality_options
        size_hint_y: None
        height: 50

    TextInput:
        id: save_path
        hint_text: 'مجلد الحفظ'
        text: root.default_save_path
        multiline: False
        size_hint_y: None
        height: 50

    Button:
        id: download_btn
        text: 'تحميل'
        on_press: root.start_download()
        background_color: 0.537, 0.706, 0.980, 1
        color: 0.118, 0.118, 0.180, 1
        disabled: True

    ProgressBar:
        id: progress_bar
        max: 100
        value: 0

    Label:
        id: status_label
        text: 'جاهز'
        size_hint_y: None
        height: 30

    Label:
        id: speed_label
        text: ''
        size_hint_y: None
        height: 30

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: 50

        Button:
            text: 'الإعدادات'
            on_press: root.open_settings()
            background_color: 0.271, 0.278, 0.333, 1

        Button:
            text: 'تحديثات'
            on_press: root.check_updates()
            background_color: 0.271, 0.278, 0.333, 1
"""


class Frame(BoxLayout):
    pass


class VDownloaderGUI(BoxLayout):
    url_input = ObjectProperty(None)
    analyze_btn = ObjectProperty(None)
    title_label = ObjectProperty(None)
    duration_label = ObjectProperty(None)
    quality_spinner = ObjectProperty(None)
    download_btn = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    status_label = ObjectProperty(None)
    speed_label = ObjectProperty(None)
    save_path = ObjectProperty(None)

    info_hidden = True
    quality_options = []
    default_save_path = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_info = None
        self.proxy_manager = ProxyManager()
        self.cookie_manager = CookieManager()
        self.downloader = None
        self._cancelled = False

        Builder.load_string(KV)
        self.init_defaults()

    def init_defaults(self):
        if os.name == 'nt':
            self.default_save_path = os.path.join(os.path.expanduser("~"), "Downloads")
        else:
            self.default_save_path = "/storage/emulated/0/Download"

    def analyze_video(self):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "يرجى إدخال رابط الفيديو"
            return

        self.status_label.text = "جاري فحص الفيديو..."
        self.analyze_btn.disabled = True

        thread = threading.Thread(target=self._analyze_worker, args=(url,))
        thread.start()

    def _analyze_worker(self, url):
        proxy = self.proxy_manager.get_selected_proxy()
        cookies = self.cookie_manager.get_cookies()

        try:
            info = VideoInfo.get_info(url, proxy, cookies)
            Clock.schedule_once(lambda dt: self._on_analyze_finished(info))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_analyze_error(str(e)))

    def _on_analyze_finished(self, info):
        self.video_info = info
        self.title_label.text = f"العنوان: {info.get('title', '')}"

        duration = info.get('duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        self.duration_label.text = f"المدة: {minutes}:{seconds:02d}"

        self.quality_options = []
        formats = info.get('formats', [])
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

                self.quality_options.append(label)

        self.quality_options.sort(
            key=lambda x: int(x.split('p')[0].split('-')[0]) if x and x[0].isdigit() else 0,
            reverse=True
        )

        if not self.quality_options:
            self.quality_options = ["الأفضل متاح"]

        self.quality_spinner.values = self.quality_options
        self.quality_spinner.text = self.quality_options[0]

        self.info_hidden = False
        self.download_btn.disabled = False
        self.status_label.text = "تم فحص الفيديو بنجاح"
        self.analyze_btn.disabled = True

    def _on_analyze_error(self, error):
        self.status_label.text = f"خطأ: {error}"
        self.analyze_btn.disabled = True

    def start_download(self):
        if not self.video_info:
            return

        quality = self.quality_spinner.text
        if "4K" in quality:
            format_id = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
        elif "1080" in quality:
            format_id = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif "720" in quality:
            format_id = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif "480" in quality:
            format_id = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        else:
            format_id = "best"

        output_path = self.save_path.text or self.default_save_path
        proxy = self.proxy_manager.get_selected_proxy()
        cookies = self.cookie_manager.get_cookies()

        self.download_btn.text = "إلغاء"
        self.download_btn.bind(on_press=lambda x: self.cancel_download())
        self.status_label.text = "جاري التحميل..."

        self.downloader = Downloader(
            self.url_input.text,
            format_id,
            output_path,
            proxy,
            cookies,
            progress_callback=self._on_progress,
            finished_callback=self._on_finished,
            error_callback=self._on_error
        )
        self.downloader.start()

    def _on_progress(self, percent, speed):
        self.progress_bar.value = percent
        self.speed_label.text = f"السرعة: {speed}"

    def _on_finished(self, filepath, title):
        self.progress_bar.value = 100
        self.status_label.text = "تم التحميل بنجاح"
        self.download_btn.text = "تحميل"
        self.download_btn.unbind(on_press=self.cancel_download)
        self.download_btn.bind(on_press=lambda x: self.start_download())
        self.download_btn.disabled = False

        show_download_complete(title, filepath)

    def _on_error(self, error):
        self.progress_bar.value = 0
        self.status_label.text = f"خطأ: {error}"
        self.download_btn.text = "تحميل"
        self.download_btn.unbind(on_press=self.cancel_download)
        self.download_btn.bind(on_press=lambda x: self.start_download())
        self.download_btn.disabled = False

        show_download_error(error)

    def cancel_download(self):
        if self.downloader:
            self.downloader.cancel()
            self.status_label.text = "تم الإلغاء"
            self.progress_bar.value = 0
            self.download_btn.text = "تحميل"
            self.disabled = False

    def open_settings(self):
        from gui.settings_dialog import SettingsDialogGUI
        App.get_running_app().root_window.add_widget(SettingsDialogGUI())

    def check_updates(self):
        from utils.updater import check_for_updates
        check_for_updates(self)


class SettingsDialogGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15


if __name__ == "__main__":
    VDownloaderGUI().run()