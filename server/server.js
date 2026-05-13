const express = require('express');
const cors = require('cors');
const ytdl = require('ytdl-core');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

const DOWNLOAD_DIR = path.join(__dirname, 'downloads');

if (!fs.existsSync(DOWNLOAD_DIR)) {
    fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });
}

const progressData = {};
const downloadTasks = {};

async function getVideoInfo(url, proxy = null) {
    const options = {};
    if (proxy) {
        options.requestOptions = {
            proxy: proxy
        };
    }

    const info = await ytdl.getInfo(url, options);

    const formats = [];
    for (const f of info.formats) {
        const filesize = f.filesize || f.filesize_approx || 0;
        const ext = f.mimeLine ? f.mimeLine.split(';')[0].split('/')[1] : f.container || 'unknown';

        if (f.hasVideo && f.hasAudio) {
            formats.push({
                format_id: f.itag,
                ext: ext,
                height: f.height || 0,
                filesize: filesize,
                format_note: f.qualityLabel || '',
            });
        } else if (f.hasVideo && !f.hasAudio) {
            formats.push({
                format_id: f.itag,
                ext: ext,
                height: f.height || 0,
                filesize: filesize,
                format_note: f.qualityLabel || '',
            });
        } else if (f.hasAudio && !f.hasVideo) {
            formats.push({
                format_id: f.itag,
                ext: ext,
                height: 0,
                filesize: filesize,
                format_note: 'audio',
            });
        }
    }

    formats.sort((a, b) => b.height - a.height);

    return {
        title: info.videoDetails.title,
        thumbnail: info.videoDetails.thumbnails[info.videoDetails.thumbnails.length - 1]?.url || '',
        duration: parseInt(info.videoDetails.lengthSeconds) || 0,
        formats: formats,
        uploader: info.videoDetails.author.name || '',
        upload_date: info.videoDetails.uploadDate || '',
    };
}

function downloadVideo(url, formatId, taskId, proxy = null) {
    const taskDir = path.join(DOWNLOAD_DIR, taskId);
    
    if (!fs.existsSync(taskDir)) {
        fs.mkdirSync(taskDir, { recursive: true });
    }

    const options = {
        filter: formatId === 'best' ? 'audioandvideo' : formatId.includes('audio') ? 'audioonly' : 'videoonly',
    };

    if (proxy) {
        options.requestOptions = {
            proxy: proxy
        };
    }

    progressData[taskId] = { percent: 0, status: 'downloading' };
    downloadTasks[taskId] = { status: 'downloading' };

    const stream = ytdl(url, options);
    let downloadedBytes = 0;
    let totalBytes = 0;

    stream.on('response', (response) => {
        totalBytes = parseInt(response.headers['content-length']) || 0;
    });

    stream.on('progress', (chunkLength, downloaded, total) => {
        downloadedBytes = downloaded;
        if (total > 0) {
            progressData[taskId] = {
                percent: (downloaded / total) * 100,
                downloaded: downloaded,
                total: total,
                status: 'downloading'
            };
        }
    });

    const ext = formatId === 'best' ? 'mp4' : 'mp4';
    const tempPath = path.join(taskDir, `temp_${taskId}.${ext}`);
    const writeStream = fs.createWriteStream(tempPath);

    stream.pipe(writeStream);

    writeStream.on('finish', () => {
        const filename = path.join(taskDir, `video.${ext}`);
        
        try {
            fs.renameSync(tempPath, filename);
            downloadTasks[taskId] = { status: 'ready', filename: filename };
            progressData[taskId] = { percent: 100, status: 'finished', filename: filename };
        } catch (err) {
            downloadTasks[taskId] = { status: 'error', error: err.message };
            progressData[taskId] = { status: 'error', error: err.message };
        }
    });

    stream.on('error', (err) => {
        downloadTasks[taskId] = { status: 'error', error: err.message };
        progressData[taskId] = { status: 'error', error: err.message };
    });
}

app.post('/api/info', async (req, res) => {
    const { url, proxy } = req.body;

    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }

    try {
        const info = await getVideoInfo(url, proxy);
        res.json(info);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/download', (req, res) => {
    const { url, format_id, proxy } = req.body;

    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }

    const taskId = uuidv4();
    
    downloadVideo(url, format_id || 'best', taskId, proxy);

    res.json({ task_id: taskId });
});

app.get('/api/status/:taskId', (req, res) => {
    const { taskId } = req.params;

    if (!downloadTasks[taskId]) {
        return res.status(404).json({ error: 'Task not found' });
    }

    const status = downloadTasks[taskId];
    const progress = progressData[taskId] || {};

    res.json({
        status: status.status,
        progress: progress,
    });
});

app.get('/api/stream/:taskId', (req, res) => {
    const { taskId } = req.params;

    if (!downloadTasks[taskId]) {
        return res.status(404).json({ error: 'Task not found' });
    }

    const task = downloadTasks[taskId];
    if (task.status !== 'ready') {
        return res.status(400).json({ error: 'File not ready' });
    }

    const filename = task.filename;
    if (!fs.existsSync(filename)) {
        return res.status(404).json({ error: 'File not found' });
    }

    const fileSize = fs.statSync(filename).size;
    const range = req.headers.range;

    if (range) {
        const parts = range.replace(/bytes=/, '').split('-');
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
        const chunkSize = end - start + 1;

        const fileStream = fs.createReadStream(filename, { start, end });
        
        const head = {
            'Content-Range': `bytes ${start}-${end}/${fileSize}`,
            'Accept-Ranges': 'bytes',
            'Content-Length': chunkSize,
            'Content-Type': 'video/mp4',
        };

        res.writeHead(206, head);
        fileStream.pipe(res);
    } else {
        const head = {
            'Content-Length': fileSize,
            'Content-Type': 'video/mp4',
            'Content-Disposition': `attachment; filename="${path.basename(filename)}"`,
        };

        res.writeHead(200, head);
        fs.createReadStream(filename).pipe(res);
    }
});

app.get('/api/file/:taskId', (req, res) => {
    const { taskId } = req.params;

    if (!downloadTasks[taskId]) {
        return res.status(404).json({ error: 'Task not found' });
    }

    const task = downloadTasks[taskId];
    if (task.status !== 'ready') {
        return res.status(400).json({ error: 'File not ready' });
    }

    const filename = task.filename;
    if (!fs.existsSync(filename)) {
        return res.status(404).json({ error: 'File not found' });
    }

    res.download(filename, path.basename(filename));
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
});