# VDownloader

A powerful video downloader application for Android and Desktop. Download videos from YouTube and 1700+ websites in multiple quality options.

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Android%20%26%20Desktop-blue" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.12%2B-yellow" alt="Python">
</p>

## Features

- **1700+ Sites Supported** - YouTube, Facebook, Instagram, Twitter, TikTok, Vimeo, Dailymotion, and more
- **Multiple Quality Options** - 4K, FHD, HD, SD, and audio-only downloads
- **Proxy Support** - Use proxies for downloading
- **Cookie Authentication** - Login to download private videos
- **Background Downloads** - Continue downloading when app is minimized (Android)
- **Progress Notifications** - Real-time download progress (Android)
- **Dark Modern UI** - Beautiful dark theme interface
- **Cross-Platform** - Works on Android and Desktop (Windows, Linux, macOS)

## Screenshots

| Android | Desktop |
|---------|---------|
| ![Android](.github/screenshots/android.png) | ![Desktop](.github/screenshots/desktop.png) |

## Installation

### Android

Download the latest APK from [GitHub Releases](https://github.com/TheWolfSy/vdownloader/releases):

```
VDownloader-v1.0.0.apk
```

Install on your device and launch the app.

### Desktop

#### Requirements

- Python 3.12 or higher
- PyQt6
- FFmpeg (for video merging)

#### Steps

1. Clone the repository:
```bash
git clone https://github.com/TheWolfSy/vdownloader.git
cd vdownloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

4. Run the app:
```bash
cd VDownloader
python main.py
```

## Usage

1. **Paste Video URL** - Copy the video link and paste it in the input field
2. **Analyze** - Tap "فحص الفيديو" to get video information
3. **Select Quality** - Choose your preferred quality (4K, FHD, HD, SD, Mp3)
4. **Download** - Tap download button to start downloading

### Supported Quality Labels

| Label | Resolution | Description |
|-------|------------|-------------|
| 4K | 2160p | Ultra HD |
| FHD | 1080p | Full HD |
| HD | 720p | HD |
| SD | 480p | Standard |
| Mp3 | Audio | Audio only |

## Supported Sites

VDownloader uses **yt-dlp** for downloading, supporting 1700+ websites including:

- **YouTube** - youtube.com, youtu.be
- **Facebook** - facebook.com, fb.watch
- **Instagram** - instagram.com
- **Twitter/X** - x.com, twitter.com
- **TikTok** - tiktok.com
- **Vimeo** - vimeo.com
- **Dailymotion** - dailymotion.com
- **Bilibili** - bilibili.com
- **Netflix** - netflix.com
- **Shahid** - shahid.net
- And many more...

Full list: [yt-dlp Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## Project Structure

```
vdownloader/
├── android/                    # Android app source
│   ├── main.py                # Kivy app entry
│   ├── buildozer.spec        # Buildozer configuration
│   └── gui/                  # Android UI
├── VDownloader/               # Desktop app source
│   ├── main.py               # Desktop entry point
│   ├── gui/                 # Desktop UI (PyQt6)
│   └── core/                # Desktop core modules
├── gui/                     # Shared UI components
├── core/                   # Core download modules
├── utils/                   # Utility functions
└── .github/
    └── workflows/           # GitHub Actions
```

## Building from Source

### Android APK

The app includes GitHub Actions workflow for automatic APK building:

1. Go to [Actions](https://github.com/TheWolfSy/vdownloader/actions)
2. Select the latest workflow run
3. Download the built APK from Artifacts

Or build locally:

```bash
cd android
pip install buildozer
buildozer android debug
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Core download engine
- [Kivy](https://kivy.org) - Open source Python framework for Android
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt) - Desktop UI framework

## Support

If you encounter any issues or have questions:

- Open an [Issue](https://github.com/TheWolfSy/vdownloader/issues)
- Check existing issues first

## Version

Current version: **1.0.0**

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/TheWolfSy">TheWolfSy</a>
</p>