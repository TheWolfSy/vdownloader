import subprocess
import shutil
import os


class FFmpegChecker:
    @staticmethod
    def check():
        os.environ['PATH'] = r"C:\ffmpeg\bin" + os.pathsep + os.environ.get('PATH', '')
        
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        
        if ffmpeg_path and ffprobe_path:
            return True, ffmpeg_path, ffprobe_path
        
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                ffmpeg_dir = os.path.dirname(path)
                ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe.exe")
                if os.path.exists(ffprobe_path):
                    return True, path, ffprobe_path
        
        return False, None, None

    @staticmethod
    def get_version():
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                first_line = result.stdout.split('\n')[0]
                return first_line
        except Exception:
            pass
        return None