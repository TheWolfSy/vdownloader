(function() {
    'use strict';

    const API_BASE = 'http://localhost:3000';

    let currentFormats = [];
    let selectedFormat = null;
    let taskId = null;
    let pollInterval = null;
    let isCapacitor = false;

    async function init() {
        if (window.Capacitor) {
            isCapacitor = true;
            await window.Capacitor.Plugins.StatusBar?.setBackgroundColor({ color: '#1a1b26' });
            await window.Capacitor.Plugins.StatusBar?.setStyle({ style: 'DARK' });
        }

        document.getElementById('getInfoBtn').addEventListener('click', getVideoInfo);
        document.getElementById('downloadBtn').addEventListener('click', startDownload);
        document.getElementById('openProModal').addEventListener('click', showProMessage);
    }

    function showError(msg) {
        const errorEl = document.getElementById('error');
        errorEl.textContent = msg;
        errorEl.classList.add('show');
        document.getElementById('loader').classList.remove('show');
        setTimeout(() => errorEl.classList.remove('show'), 5000);
    }

    function clearError() {
        document.getElementById('error').textContent = '';
        document.getElementById('error').classList.remove('show');
    }

    function showLoader(show) {
        const loader = document.getElementById('loader');
        if (show) {
            loader.classList.add('show');
        } else {
            loader.classList.remove('show');
        }
    }

    function setButtonLoading(btnId, loading) {
        const btn = document.getElementById(btnId);
        btn.disabled = loading;
    }

    async function getVideoInfo() {
        clearError();
        const url = document.getElementById('videoUrl').value.trim();
        const proxy = document.getElementById('proxy').value.trim();

        if (!url) {
            showError('Please enter a video URL');
            return;
        }

        showLoader(true);
        setButtonLoading('getInfoBtn', true);
        hideVideoInfo();

        try {
            const response = await fetch(`${API_BASE}/api/info`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, proxy })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch video info');
            }

            displayVideoInfo(data);
        } catch (e) {
            showError(e.message);
        } finally {
            showLoader(false);
            setButtonLoading('getInfoBtn', false);
        }
    }

    function displayVideoInfo(info) {
        const videoInfoEl = document.getElementById('videoInfo');
        const titleEl = document.getElementById('videoTitle');
        const detailsEl = document.getElementById('videoDetails');

        titleEl.textContent = info.title || 'Unknown Title';

        const duration = info.duration || 0;
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        detailsEl.textContent = `Duration: ${minutes}:${seconds.toString().padStart(2, '0')} | Uploader: ${info.uploader || 'Unknown'}`;

        currentFormats = info.formats || [];
        const formatsList = document.getElementById('formatsList');
        formatsList.innerHTML = '';

        if (currentFormats.length === 0) {
            showError('No formats available for this video');
            return;
        }

        currentFormats.forEach((format, index) => {
            const item = document.createElement('div');
            item.className = 'format-item';
            item.dataset.index = index;

            const size = format.filesize > 0 ? format.filesize / (1024 * 1024) : 0;
            const sizeStr = size > 0 ? `${size.toFixed(1)} MB` : 'Unknown';

            item.innerHTML = `
                <span class="format-info">${format.height}p (${format.ext || 'mp4'})</span>
                <span class="format-size">${sizeStr}</span>
            `;

            item.addEventListener('click', () => selectFormat(index));
            formatsList.appendChild(item);
        });

        if (currentFormats.length > 0) {
            selectFormat(0);
        }

        videoInfoEl.classList.add('show');
    }

    function selectFormat(index) {
        selectedFormat = currentFormats[index];

        document.querySelectorAll('.format-item').forEach((item, i) => {
            if (i === index) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    function hideVideoInfo() {
        document.getElementById('videoInfo').classList.remove('show');
        document.getElementById('progressContainer').classList.remove('show');
    }

    async function startDownload() {
        const url = document.getElementById('videoUrl').value.trim();
        const proxy = document.getElementById('proxy').value.trim();

        if (!selectedFormat) {
            showError('Please select a quality');
            return;
        }

        hideVideoInfo();
        showProgress(true);
        clearError();

        try {
            const response = await fetch(`${API_BASE}/api/download`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url,
                    format_id: selectedFormat.format_id,
                    proxy
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to start download');
            }

            taskId = data.task_id;
            pollProgress();
        } catch (e) {
            showError(e.message);
            showProgress(false);
        }
    }

    function showProgress(show) {
        const container = document.getElementById('progressContainer');
        if (show) {
            container.classList.add('show');
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressText').textContent = 'Starting download...';
        } else {
            container.classList.remove('show');
        }
    }

    function pollProgress() {
        if (pollInterval) {
            clearInterval(pollInterval);
        }

        pollInterval = setInterval(async () => {
            if (!taskId) {
                clearInterval(pollInterval);
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/api/status/${taskId}`);
                const data = await response.json();

                const percent = data.progress?.percent || 0;
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');

                progressFill.style.width = `${percent}%`;
                progressText.textContent = `Downloading... ${Math.round(percent)}%`;

                if (data.status === 'ready') {
                    clearInterval(pollInterval);
                    progressFill.style.width = '100%';
                    progressText.textContent = 'Processing...';
                    downloadFile();
                } else if (data.status === 'error') {
                    clearInterval(pollInterval);
                    showError(data.progress?.error || 'Download failed');
                    showProgress(false);
                }
            } catch (e) {
                clearInterval(pollInterval);
                showError(e.message);
                showProgress(false);
            }
        }, 1000);
    }

    async function downloadFile() {
        const progressText = document.getElementById('progressText');
        progressText.textContent = 'Downloading video...';

        try {
            const response = await fetch(`${API_BASE}/api/stream/${taskId}`);

            if (!response.ok) {
                throw new Error('Failed to download video');
            }

            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'video.mp4';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (match) {
                    filename = match[1].replace(/['"]/g, '');
                }
            }

            const blob = await response.blob();

            if (isCapacitor && window.Capacitor.Plugins) {
                await saveWithCapacitor(blob, filename);
            } else {
                downloadBrowser(blob, filename);
            }

            progressText.textContent = 'Download complete!';
            progressText.classList.add('progress-success');

            setTimeout(() => {
                showProgress(false);
                progressText.classList.remove('progress-success');
            }, 3000);

        } catch (e) {
            showError(e.message);
            showProgress(false);
        }
    }

    function downloadBrowser(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    async function saveWithCapacitor(blob, filename) {
        try {
            const arrayBuffer = await blob.arrayBuffer();
            const base64 = arrayBufferToBase64(arrayBuffer);

            const Filesystem = window.Capacitor.Plugins.Filesystem;
            const result = await Filesystem.writeFile({
                path: filename,
                data: base64,
                directory: 'Documents',
                encoding: 'base64'
            });

            document.getElementById('progressText').textContent = 'File saved!';

            if (window.Capacitor.Plugins.Share) {
                await window.Capacitor.Plugins.Share.share({
                    title: 'Downloaded Video',
                    text: filename,
                    url: result.uri,
                    dialogTitle: 'Share Video'
                });
            }
        } catch (e) {
            console.error('Capacitor save error:', e);
            downloadBrowser(blob, filename);
        }
    }

    function arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    function showProMessage() {
        if (isCapacitor && window.Capacitor.Plugins?.Toast) {
            window.Capacitor.Plugins.Toast.show({
                text: 'Pro features coming soon!',
                duration: 'short'
            });
        } else {
            alert('Pro features coming soon!');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();