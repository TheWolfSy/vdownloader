import sys
import os
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder

Window.softinput_mode = "pan"


class VDownloaderApp(App):
    title = "VDownloader"

    def build(self):
        from gui.main_window import VDownloaderGUI
        return VDownloaderGUI()

    def on_pause(self):
        return True


if __name__ == "__main__":
    VDownloaderApp().run()