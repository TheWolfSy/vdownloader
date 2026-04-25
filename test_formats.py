import os
import sys
import yt_dlp

sys.path.insert(0, '.')
os.environ['PATH'] = r"C:\ffmpeg\bin;" + os.environ.get('PATH', '')

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info('https://youtu.be/3QKp_QERll8', download=False)
    print(f"Title: {info.get('title')}")
    print(f"Duration: {info.get('duration')}")
    print("\nAvailable Formats:")
    for f in info.get('formats', [])[:15]:
        height = f.get('height', 0)
        vcodec = f.get('vcodec', 'none')
        ext = f.get('ext', '')
        fid = f.get('format_id', '')
        print(f"  {height}p - {fid} - {ext} - Video: {vcodec != 'none'}")