import os
from flask import Flask, request, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
import yt_dlp
import threading
import uuid

app = Flask(__name__, static_folder='static')
CORS(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

progress_data = {}
download_tasks = {}


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


def get_video_info(url, proxy=None, cookies=None):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    if proxy:
        ydl_opts['proxy'] = proxy
    if cookies:
        ydl_opts['cookiefile'] = cookies
    
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
                        'format_note': format_note,
                    })
            elif f.get('acodec', 'none') != 'none':
                formats.append({
                    'format_id': f['format_id'],
                    'ext': ext,
                    'height': 0,
                    'filesize': filesize,
                    'format_note': format_note,
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


def progress_hook(d, task_id):
    if task_id in progress_data:
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                progress_data[task_id] = {
                    'percent': (downloaded / total) * 100,
                    'speed': d.get('speed', 0),
                    'filename': d.get('filename', ''),
                }
        elif d['status'] == 'finished':
            progress_data[task_id] = {'percent': 100, 'status': 'finished'}


def download_video(url, format_id, task_id, proxy=None, cookies=None):
    task_dir = os.path.join(DOWNLOAD_DIR, task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(task_dir, '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: progress_hook(d, task_id)],
        'merge_output_format': 'mp4',
    }
    
    if proxy:
        ydl_opts['proxy'] = proxy
    if cookies:
        ydl_opts['cookiefile'] = cookies
    
    try:
        progress_data[task_id] = {'percent': 0, 'status': 'downloading'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            download_tasks[task_id] = {'status': 'ready', 'filename': filename}
    except Exception as e:
        download_tasks[task_id] = {'status': 'error', 'error': str(e)}
        progress_data[task_id] = {'status': 'error', 'error': str(e)}


@app.route('/api/info', methods=['POST'])
def api_info():
    data = request.json
    url = data.get('url')
    proxy = data.get('proxy')
    cookies = data.get('cookies')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        info = get_video_info(url, proxy, cookies)
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def api_download():
    data = request.json
    url = data.get('url')
    format_id = data.get('format_id', 'best')
    proxy = data.get('proxy')
    cookies = data.get('cookies')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=download_video, args=(url, format_id, task_id, proxy, cookies))
    thread.start()
    
    return jsonify({'task_id': task_id})


@app.route('/api/status/<task_id>')
def api_status(task_id):
    if task_id not in download_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    status = download_tasks[task_id]
    progress = progress_data.get(task_id, {})
    
    return jsonify({
        'status': status.get('status', 'unknown'),
        'progress': progress,
    })


@app.route('/api/file/<task_id>')
def api_file(task_id):
    if task_id not in download_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = download_tasks[task_id]
    if task.get('status') != 'ready':
        return jsonify({'error': 'File not ready'}), 400
    
    filename = task['filename']
    if not os.path.exists(filename):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filename, as_attachment=True)


@app.route('/api/stream/<task_id>')
def api_stream(task_id):
    if task_id not in download_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = download_tasks[task_id]
    if task.get('status') != 'ready':
        return jsonify({'error': 'File not ready'}), 400
    
    filename = task['filename']
    if not os.path.exists(filename):
        return jsonify({'error': 'File not found'}), 404
    
    file_size = os.path.getsize(filename)
    
    def generate():
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
    
    response = Response(generate(), mimetype='video/mp4')
    response.headers['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
    response.headers['Content-Length'] = file_size
    
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)