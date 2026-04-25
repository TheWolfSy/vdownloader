import sys
import platform
import os


def detect_platform():
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        if 'ANDROID' in os.environ:
            return 'android'
        return 'linux'
    return 'unknown'


def main():
    app_platform = detect_platform()

    if app_platform == 'android':
        from android.main import VDownloaderApp
        VDownloaderApp().run()
    else:
        from PyQt6.QtWidgets import QApplication
        from gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        window = MainWindow()
        window.show()

        sys.exit(app.exec())


if __name__ == "__main__":
    main()