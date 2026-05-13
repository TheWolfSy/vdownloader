<div align="center">
  <img src="web_app/static/vdownloader_logo.svg" alt="vdownloader" width="300"/>
</div>

# 🐺 vdownloader

Download YouTube videos in high quality — Web app + Mobile app (Capacitor) + Node.js server

## 🌟 Features

- **Download video** in multiple qualities (1080p, 720p, 480p, audio only)
- **Web interface** (Flask) for desktop browsers
- **Mobile app** (Capacitor) for Android & iOS
- **Local Node.js server** runs on your phone via Termux
- **Proxy support** for VPN/Proxy connections
- **Dark theme** — modern and sleek

## 📁 Project Structure

```
vdownloader/
├── mobile-app/               # Capacitor app (Android/iOS)
│   ├── www/                  # Vanilla JS frontend
│   │   ├── index.html
│   │   ├── app.js
│   │   └── styles.css
│   ├── android/              # Native Android project
│   ├── capacitor.config.json # Capacitor configuration
│   └── package.json          # npm dependencies
│
├── server/                   # Node.js server (Express + ytdl-core)
│   ├── server.js             # Entry point
│   └── package.json
│
├── web_app/                  # Flask web app (legacy)
│   ├── app.py
│   └── static/
│       ├── index.html
│       └── theme.css
│
└── README.md
```

## 🚀 Getting Started

### Flask Web App

```bash
cd web_app
pip install -r ../requirements.txt
python app.py
```

### Node.js Server (for mobile app)

```bash
cd server
npm install
node server.js
```

### Capacitor Mobile App

```bash
cd mobile-app
npm install
npx cap sync android
npx cap open android
```

## 📦 Releases

| Version | Date | Link |
|---------|------|------|
| **v1.0.0** — Initial Release | 2026-05-13 | [Download APK](https://github.com/TheWolfSy/vdownloader/releases/tag/v1.0.0) |

Includes Android APK (`vdownloader-v1.0.0.apk`) for sideloading.  
[View all releases →](https://github.com/TheWolfSy/vdownloader/releases)

## 📱 Usage on Phone

1. Open **Termux** on Android
2. Start the Node.js server:
   ```bash
   cd server
   node server.js
   ```
3. Open the vdownloader app — it auto‑connects to `localhost:3000`

## 🔧 Tech Stack

| Tech | Purpose |
|------|---------|
| **Capacitor** | Mobile app (Android / iOS) |
| **Node.js + Express** | Download API server |
| **ytdl-core** | YouTube video download |
| **Vanilla JS** | User interface |
| **Flask (legacy)** | Original web app |

## 📄 License

MIT License
