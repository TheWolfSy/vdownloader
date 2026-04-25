import os
import yt_dlp


class VideoInfo:
    _initialized = False
    
    @classmethod
    def _init_ffmpeg(cls):
        if cls._initialized:
            return
        ffmpeg_path = r"C:\ffmpeg\bin"
        if os.path.exists(ffmpeg_path):
            os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ.get('PATH', '')
        cls._initialized = True
    
    @staticmethod
    def get_info(url, proxy=None, cookies=None):
        VideoInfo._init_ffmpeg()
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        if proxy:
            ydl_opts['proxy'] = proxy
        
        if cookies:
            ydl_opts['cookiefile'] = cookies
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                formats = []
                for f in info.get('formats', []):
                    format_note = f.get('format_note', '')
                    ext = f.get('ext', '')
                    filesize = f.get('filesize', 0) or f.get('filesize_approx', 0)
                    
                    if f.get('vcodec', 'none') != 'none':
                        height = f.get('height', 0)
                        if height:
                            formats.append({
                                'format_id': f['format_id'],
                                'ext': ext,
                                'height': height,
                                'filesize': filesize,
                            })
                    elif f.get('acodec', 'none') != 'none':
                        formats.append({
                            'format_id': f['format_id'],
                            'ext': ext,
                            'height': 0,
                            'filesize': filesize,
                        })
                
                formats.sort(key=lambda x: x['height'], reverse=True)
                
                return {
                    'title': info.get('title', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration', 0),
                    'formats': formats,
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                }
        except Exception as e:
            raise Exception(f"فشل في جلب المعلومات: {str(e)}")