import os
import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    progress = pyqtSignal(float, str, str)
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)
    
    def __init__(self, url, format_id, output_path, proxy=None, cookies=None):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.output_path = output_path
        self.proxy = proxy
        self.cookies = cookies
        self._cancelled = False
        
        ffmpeg_path = r"C:\ffmpeg\bin"
        if os.path.exists(ffmpeg_path):
            os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ.get('PATH', '')
    
    def cancel(self):
        self._cancelled = True
    
    def run(self):
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
        
        if self.cookies:
            ydl_opts['cookiefile'] = self.cookies
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                output_file = ydl.prepare_filename(info)
                
                if self._cancelled and os.path.exists(output_file):
                    os.remove(output_file)
                    self.error.emit("تم إلغاء التحميل")
                elif os.path.exists(output_file):
                    self.finished.emit(output_file, info.get('title', 'Video'))
                else:
                    self.finished.emit(output_file, info.get('title', 'Video'))
        except Exception as e:
            self.error.emit(str(e))
    
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
                self.progress.emit(percent, speed_str, d.get('filename', ''))
        
        elif d['status'] == 'finished':
            self.progress.emit(100, "Completed", d.get('filename', ''))
    
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