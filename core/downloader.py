import os
import threading
import yt_dlp
import platform


class Downloader:
    def __init__(self, url, format_id, output_path, proxy=None, cookies=None,
                 progress_callback=None, finished_callback=None, error_callback=None):
        self.url = url
        self.format_id = format_id
        self.output_path = output_path
        self.proxy = proxy
        self.cookies = cookies
        self.progress_callback = progress_callback
        self.finished_callback = finished_callback
        self.error_callback = error_callback
        self._cancelled = False
        self._thread = None
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def cancel(self):
        self._cancelled = True
        self._running = False

    def _run(self):
    format_id = self.format_id.lower()
    is_audio_only = ('audio' in format_id or 
                    'mp3' in format_id or 
                    'bestaudio' in format_id or
                    format_id == 'best' and 'video' not in format_id)

    ydl_opts = {
        'format': self.format_id,
        'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [self._progress_hook],
    }

    if is_audio_only:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        ydl_opts['outtmpl'] = os.path.join(self.output_path, '%(title)s.mp3')
    else:
        ydl_opts['merge_output_format'] = 'mp4'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegMetadata',
        }]

        if self.proxy:
            ydl_opts['proxy'] = self.proxy

        if self.cookies and os.path.exists(self.cookies):
            ydl_opts['cookiefile'] = self.cookies

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                output_file = ydl.prepare_filename(info)

                if self._cancelled and os.path.exists(output_file):
                    os.remove(output_file)
                    if self.error_callback:
                        self.error_callback("تم إلغاء التحميل")
                elif os.path.exists(output_file):
                    if self.finished_callback:
                        self.finished_callback(output_file, info.get('title', 'Video'))
                else:
                    if self.finished_callback:
                        self.finished_callback(output_file, info.get('title', 'Video'))
        except Exception as e:
            if self.error_callback:
                self.error_callback(str(e))
        finally:
            self._running = False

    def _progress_hook(self, d):
        if self._cancelled:
            d['stop'] = True
            return

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)

            if total > 0:
                percent = (downloaded / total) * 100
                speed = d.get('speed', 0)
                speed_str = self._format_speed(speed) if speed else "0 B/s"
                if self.progress_callback:
                    self.progress_callback(percent, speed_str, d.get('filename', ''))

        elif d['status'] == 'finished':
            if self.progress_callback:
                self.progress_callback(100, "Completed", d.get('filename', ''))

    @staticmethod
    def _format_speed(speed):
        if speed is None:
            return "0 B/s"
        if speed >= 1024 * 1024:
            return f"{speed / (1024 * 1024):.1f} MB/s"
        elif speed >= 1024:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed:.0f} B/s"


class BackgroundDownloader:
    @staticmethod
    def start_background(url, format_id, output_path, proxy=None, cookies=None):
        if platform.system() == 'Android':
            try:
                from jnius import autoclass
                WorkManager = autoclass('androidx.work.WorkManager')
                OneTimeWorkRequestBuilder = autoclass('androidx.work.OneTimeWorkRequest$Builder')
                Constraints = autoclass('androidx.work.Constraints$Builder')
                NetworkType = autoclass('androidx.work.NetworkType')

                constraints = (Constraints()
                    .setRequiredNetworkType(NetworkType.UNMETERED)
                    .build())

                download_request = (OneTimeWorkRequestBuilder
                    .addTag('vdownloader')
                    .build())

                WorkManager.getInstance().enqueueUniqueWork(
                    'vdownloader_download',
                    1,
                    download_request
                )
            except Exception:
                pass

        downloader = Downloader(url, format_id, output_path, proxy, cookies)
        downloader.start()
        return downloader


if __name__ == "__main__":
    d = Downloader(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "best",
        ".",
        progress_callback=lambda p, s, f: print(f"{p}% - {s}"),
        finished_callback=lambda f, t: print(f"Done: {t}"),
        error_callback=lambda e: print(f"Error: {e}")
    )
    d.start()