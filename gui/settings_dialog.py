import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

from utils.proxy import ProxyManager
from utils.cookies import CookieManager


class SettingsDialogGUI(BoxLayout):
    def __init__(self, proxy_manager, cookie_manager, **kwargs):
        super().__init__(**kwargs)
        self.proxy_manager = proxy_manager
        self.cookie_manager = cookie_manager
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        self.init_ui()

    def init_ui(self):
        title = Label(
            text='الإعدادات',
            font_size='20sp',
            bold=True,
            color=(0.537, 0.706, 0.980, 1),
            size_hint_y=None,
            height=50
        )
        self.add_widget(title)

        proxy_group = self.create_proxy_section()
        self.add_widget(proxy_group)

        cookies_group = self.create_cookies_section()
        self.add_widget(cookies_group)

        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        save_btn = Button(
            text='حفظ',
            background_color=(0.537, 0.706, 0.980, 1),
            color=(0.118, 0.118, 0.180, 1)
        )
        save_btn.bind(on_press=self.save_settings)
        cancel_btn = Button(
            text='إلغاء',
            background_color=(0.271, 0.278, 0.333, 1),
            color=(0.804, 0.839, 0.957, 1)
        )
        cancel_btn.bind(on_press=self.dismiss)
        buttons.add_widget(save_btn)
        buttons.add_widget(cancel_btn)
        self.add_widget(buttons)

    def create_proxy_section(self):
        group = BoxLayout(orientation='vertical', spacing=10, padding=10)

        title = Label(
            text='إعدادات البروكسي',
            bold=True,
            color=(0.804, 0.839, 0.957, 1),
            size_hint_y=None,
            height=30
        )
        group.add_widget(title)

        self.proxy_spinner = Spinner(
            text='-- لا يوجد --',
            values=['-- لا يوجد --'],
            size_hint_y=None,
            height=40
        )
        group.add_widget(self.proxy_spinner)

        self.proxy_name_input = TextInput(
            hint_text='اسم البروكسي',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        group.add_widget(self.proxy_name_input)

        self.proxy_url_input = TextInput(
            hint_text='http://ip:port',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        group.add_widget(self.proxy_url_input)

        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        add_btn = Button(text='إضافة', size_hint_x=1)
        add_btn.bind(on_press=self.add_proxy)
        remove_btn = Button(
            text='حذف',
            background_color=(0.953, 0.545, 0.659, 1),
            color=(0.118, 0.118, 0.180, 1),
            size_hint_x=1
        )
        remove_btn.bind(on_press=self.remove_proxy)
        buttons.add_widget(add_btn)
        buttons.add_widget(remove_btn)
        group.add_widget(buttons)

        return group

    def create_cookies_section(self):
        group = BoxLayout(orientation='vertical', spacing=10, padding=10)

        title = Label(
            text='إعدادات الكوكيز',
            bold=True,
            color=(0.804, 0.839, 0.957, 1),
            size_hint_y=None,
            height=30
        )
        group.add_widget(title)

        browser_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        browser_layout.add_widget(Label(text='المتصفح:'))
        self.browser_spinner = Spinner(
            text='اكتشاف تلقائي',
            values=['اكتشاف تلقائي', 'chrome', 'firefox', 'edge'],
            size_hint_x=1
        )
        browser_layout.add_widget(self.browser_spinner)
        group.add_widget(browser_layout)

        self.cookies_status = Label(
            text='الكوكيز: غير متوفرة',
            size_hint_y=None,
            height=30
        )
        group.add_widget(self.cookies_status)

        return group

    def add_proxy(self, instance):
        name = self.proxy_name_input.text.strip()
        url = self.proxy_url_input.text.strip()

        if not name or not url:
            return

        self.proxy_manager.add_proxy(name, url)
        current = list(self.proxy_spinner.values)
        current.append(f"{name} ({url})")
        self.proxy_spinner.values = current
        self.proxy_name_input.text = ''
        self.proxy_url_input.text = ''

    def remove_proxy(self, instance):
        current_text = self.proxy_spinner.text
        if current_text == '-- لا يوجد --':
            return

        name = current_text.split(" (")[0]
        self.proxy_manager.remove_proxy(name)
        self.proxy_spinner.values = ['-- لا يوجد --']

    def save_settings(self, instance):
        browser = self.browser_spinner.text
        if browser != 'اكتشاف تلقائي':
            self.cookie_manager.set_preferred_browser(browser)
        self.dismiss(instance)

    def dismiss(self, instance):
        if self.parent:
            self.parent.remove(self.parent.children[-1])


class SettingsPopup(Popup):
    def __init__(self, proxy_manager, cookie_manager, **kwargs):
        super().__init__(**kwargs)
        content = SettingsDialogGUI(proxy_manager, cookie_manager)
        self.content = content
        self.title = 'الإعدادات'
        self.size_hint = (0.9, 0.9)


def open_settings(proxy_manager=None, cookie_manager=None):
    if proxy_manager is None:
        proxy_manager = ProxyManager()
    if cookie_manager is None:
        cookie_manager = CookieManager()

    popup = SettingsPopup(proxy_manager, cookie_manager)
    popup.open()