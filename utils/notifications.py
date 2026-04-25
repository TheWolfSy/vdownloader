import platform
import os
import threading


def show_download_complete(title, filename):
    try:
        from plyer import notification
        notification.notify(
            title="VDownloader - تم التحميل",
            message=f"تم تحميل: {title}",
            timeout=5
        )
    except Exception:
        pass


def show_download_start(title, file_size=0):
    try:
        from plyer import notification
        if file_size > 0:
            if file_size > 1024 * 1024 * 1024:
                size_str = f"{file_size / (1024**3):.1f} GB"
            elif file_size > 1024 * 1024:
                size_str = f"{file_size / (1024**2):.1f} MB"
            else:
                size_str = f"{file_size / 1024:.0f} KB"
            message = f"جاري تحميل: {title} ({size_str})"
        else:
            message = f"جاري تحميل: {title}"
        notification.notify(
            title="VDownloader",
            message=message,
            timeout=3
        )
    except Exception:
        pass


def show_download_progress(title, percent, speed):
    try:
        from plyer import notification
        notification.notify(
            title="VDownloader",
            message=f"{title}: {int(percent)}% • {speed}",
            timeout=1
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
    show_download_start("Test Video", 50000000)
    show_download_progress("Test Video", 45, "2.5 MB/s")
    show_download_error("Test Error")
    show_update_available("1.1.0")