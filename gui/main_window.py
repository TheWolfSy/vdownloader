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
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp

from core.video_info import VideoInfo
from core.downloader import Downloader
from utils.proxy import ProxyManager
from utils.cookies import CookieManager
from utils.notifications import show_download_complete, show_download_error

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

KV = """
<VDownloaderGUI>:
    orientation: 'vertical'
    padding: dp(16)
    spacing: dp(16)
    bg: '#0A0A0A'

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(60)
        justify: 'center'

        Label:
            text: 'V'
            font_size: '32sp'
            bold: True
            color: '#FFFFFF'
            size_hint_x: None
            width: dp(40)

        Label:
            text: 'DOWNLOADER'
            font_size: '18sp'
            bold: True
            letter-spacing: '4'
            color: '#FFFFFF'

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(50)
        spacing: dp(10)

        TextInput:
            id: url_input
            hint_text: 'Paste video URL'
            multiline: False
            background_color: '#141414'
            foreground_color: '#FAFAFA'
            cursor_color: '#FFFFFF'
            padding_x: dp(16)
            padding_y: dp(14)
            font_size: '14sp'

        Button:
            id: paste_btn
            text: '📋'
            size_hint_x: None
            width: dp(45)
            on_press: root.paste_url()
            background_normal: ''
            background_color: '#141414'
            color: '#808080'

    BoxLayout:
        id: preview_box
        orientation: 'vertical'
        size_hint_y: None
        height: dp(0)
        opacity: 0
        disabled: True
        spacing: dp(12)

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(80)
            spacing: dp(12)
            padding: dp(12)
            canvas:
                Color:
                    rgba: 0.039, 0.039, 0.039, 1
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [12]

            BoxLayout:
                size_hint_x: None
                width: dp(100)
                Image:
                    id: thumbnail
                    source: ''
                    allow_stretch: True
                    keep_ratio: True

            BoxLayout:
                orientation: 'vertical'
                spacing: dp(4)
                padding: dp(4)

                Label:
                    id: title_label
                    text: 'Title'
                    font_size: '13sp'
                    color: '#FAFAFA'
                    text_size: self.width, None
                    halign: 'right'
                    shorten: True
                    max_lines: 2

                Label:
                    id: duration_label
                    text: '--:--'
                    font_size: '12sp'
                    color: '#808080'

                Label:
                    id: size_label
                    text: '--'
                    font_size: '12sp'
                    color: '#808080'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(40)
            spacing: dp(8)

            Button:
                text: '↻'
                size_hint_x: None
                width: dp(40)
                on_press: root.analyze_video()
                background_normal: ''
                background_color: '#141414'
                color: '#FFFFFF'

    BoxLayout:
        id: quality_box
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(0)
        opacity: 0
        disabled: True
        spacing: dp(8)

    ScrollView:
        do_scroll_x: True
        bar_width: 0

        BoxLayout:
            orientation: 'horizontal'
            size_hint_x: None
            width: self.parent.width
            id: quality_scroll

    BoxLayout:
        id: progress_box
        orientation: 'vertical'
        size_hint_y: None
        height: dp(0)
        opacity: 0
        disabled: True
        spacing: dp(8)

        ProgressBar:
            id: progress_bar
            max: 100
            value: 0
            height: dp(4)
            background_color: '#1F1F1F'
            color: '#FFFFFF'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(20)

            Label:
                id: percent_label
                text: '0%'
                color: '#FFFFFF'

            Label:
                id: speed_label
                text: ''
                color: '#808080'

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(48)
        spacing: dp(12)

        Button:
            id: download_btn
            text: '↓ Download'
            on_press: root.start_download()
            background_normal: ''
            background_color: '#FFFFFF'
            color: '#0A0A0A'
            bold: True
            font_size: '14sp'

    Label:
        id: status_label
        text: 'Ready'
        size_hint_y: None
        height: dp(24)
        color: '#808080'
        font_size: '12sp'

    Widget:
        size_hint_y: 1

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(50)
        spacing: dp(32)
        justify: 'center'

        Button:
            text: '⬤'
            size_hint_x: None
            width: dp(40)
            on_press: root.go_home()
            background_normal: ''
            background_color: '#FFFFFF'
            color: '#0A0A0A'

        Button:
            text: '⬤'
            size_hint_x: None
            width: dp(40)
            on_press: root.go_history()
            background_normal: ''
            background_color: '#1F1F1F'
            color: '#1F1F1F'

        Button:
            text: '⚙'
            size_hint_x: None
            width: dp(40)
            on_press: root.open_settings()
            background_normal: ''
            background_color: '#1F1F1F'
            color: '#808080'
"""


class VDownloaderGUI(BoxLayout):
    url_input = ObjectProperty(None)
    download_btn = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    status_label = ObjectProperty(None)
    speed_label = ObjectProperty(None)
    title_label = ObjectProperty(None)
    duration_label = ObjectProperty(None)
    size_label = ObjectProperty(None)
    thumbnail = ObjectProperty(None)
    quality_box = ObjectProperty(None)
    preview_box = ObjectProperty(None)
    progress_box = ObjectProperty(None)
    percent_label = ObjectProperty(None)

    info_hidden = BooleanProperty(True)
    default_save_path = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_info = None
        self.selected_format = None
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

    def paste_url(self):
        from kivy.core.clipboard import Clipboard
        url = Clipboard.paste()
        if url:
            self.url_input.text = url

    def analyze_video(self):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = "Enter video URL"
            return

        self.status_label.text = "Analyzing..."
        self.download_btn.disabled = True

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
        self.title_label.text = info.get('title', 'Unknown')[:50]

        duration = info.get('duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        self.duration_label.text = f"{minutes}:{seconds:02d}"

        filesize = info.get('filesize', 0)
        if filesize > 1024 * 1024 * 1024:
            self.size_label.text = f"{filesize / (1024**3):.1f} GB"
        elif filesize > 1024 * 1024:
            self.size_label.text = f"{filesize / (1024**2):.1f} MB"
        else:
            self.size_label.text = f"{filesize / 1024:.0f} KB"

        self._build_quality_buttons(info.get('formats', [])[:5])

        self.info_hidden = False
        self.preview_box.height = dp(120)
        self.preview_box.opacity = 1
        self.preview_box.disabled = False

        self.quality_box.height = dp(44)
        self.quality_box.opacity = 1
        self.quality_box.disabled = False

        self.download_btn.disabled = False
        self.status_label.text = "Select quality & download"
        self.download_btn.text = "↓ Download"

    def _build_quality_buttons(self, formats):
        quality_box = self.ids.quality_scroll
        quality_box.clear_widgets()

        seen = set()
        quality_map = {}

        for f in formats:
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

        for idx, (label, format_id) in enumerate(quality_items):
            btn = Button(
                text=label,
                size_hint_x=None,
                width=dp(75),
                on_press=lambda x, fid=format_id, lbl=label: self._select_quality(fid, lbl)
            )
            btn.quality_id = format_id

            if idx == 0:
                btn.background_normal = ''
                btn.background_color = '#FFFFFF'
                btn.color = '#0A0A0A'
                self.selected_format = format_id
                self.selected_label = label
            else:
                btn.background_normal = ''
                btn.background_color = '#1F1F1F'
                btn.color = '#808080'

            quality_box.add_widget(btn)

        if not quality_map:
            btn = Button(text="Auto", size_hint_x=None, width=dp(75))
            btn.background_normal = ''
            btn.background_color = '#FFFFFF'
            btn.color = '#0A0A0A'
            quality_box.add_widget(btn)
            self.selected_format = "best"

    def _select_quality(self, format_id, label):
        quality_box = self.ids.quality_scroll

        for child in quality_box.children:
            if hasattr(child, 'quality_id'):
                if child.quality_id == format_id:
                    child.background_normal = ''
                    child.background_color = '#FFFFFF'
                    child.color = '#0A0A0A'
                    self.selected_format = format_id
                    self.selected_label = label
                else:
                    child.background_normal = ''
                    child.background_color = '#1F1F1F'
                    child.color = '#808080'

    def _on_analyze_error(self, error):
        self.status_label.text = f"Error: {error}"
        self.download_btn.disabled = True

    def start_download(self):
        if not self.video_info:
            return

        format_id = self.selected_format or "best"
        output_path = self.default_save_path
        proxy = self.proxy_manager.get_selected_proxy()
        cookies = self.cookie_manager.get_cookies()

        self.download_btn.text = "■ Stop"
        self.download_btn.bind(on_press=lambda x: self.cancel_download())
        self.status_label.text = "Downloading..."

        self.progress_box.height = dp(60)
        self.progress_box.opacity = 1
        self.progress_box.disabled = False

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

    def _on_progress(self, percent, speed, filename):
        self.progress_bar.value = percent
        self.percent_label.text = f"{int(percent)}%"
        self.speed_label.text = speed
        self.status_label.text = f"Downloading {int(percent)}%"

    def _on_finished(self, filepath, title):
        self.progress_bar.value = 100
        self.status_label.text = "Download complete"
        self.download_btn.text = "↓ Download"
        self.download_btn.unbind(on_press=self.cancel_download)
        self.download_btn.bind(on_press=lambda x: self.start_download())
        self.download_btn.disabled = False

        self.progress_box.height = dp(0)
        self.progress_box.opacity = 0
        self.progress_box.disabled = True

        show_download_complete(title, filepath)

    def _on_error(self, error):
        self.status_label.text = f"Error: {error}"
        self.download_btn.text = "↓ Download"
        self.download_btn.unbind(on_press=self.cancel_download)
        self.download_btn.bind(on_press=lambda x: self.start_download())
        self.download_btn.disabled = False

        self.progress_box.height = dp(0)
        self.progress_box.opacity = 0
        self.progress_box.disabled = True

        show_download_error(error)

    def cancel_download(self):
        if self.downloader:
            self.downloader.cancel()
            self.status_label.text = "Cancelled"
            self.progress_bar.value = 0
            self.download_btn.text = "↓ Download"
            self.download_btn.disabled = False

    def go_home(self):
        pass

    def go_history(self):
        pass

    def open_settings(self):
        from gui.settings_dialog import SettingsDialogGUI
        App.get_running_app().root_window.add_widget(SettingsDialogGUI())


class SettingsDialogGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)


if __name__ == "__main__":
    VDownloaderGUI().run()