import platform
import os


def show_download_complete(title, filename):
    try:
        from plyer import notification
        notification.notify(
            title="VDownloader",
            message=f"تم تحميل: {title}",
            timeout=5
        )
    except Exception:
        pass


def show_download_error(error):
    try:
        from plyer import notification
        notification.notify(
            title="VDownloader - خطأ",
            message=str(error),
            timeout=10
        )
    except Exception:
        pass


def show_update_available(version):
    try:
        from plyer import notification
        notification.notify(
            title="VDownloader - تحديث",
            message=f"إصدار جديد متاح: {version}",
            timeout=5
        )
    except Exception:
        pass


def is_android():
    return platform.system() == "Linux" and "ANDROID" in os.environ


if __name__ == "__main__":
    show_download_complete("Test Video", "/path/to/video.mp4")
    show_download_error("Test Error")
    show_update_available("1.1.0")