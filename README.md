<div align="center">
  <img src="web_app/static/vdownloader_logo.svg" alt="vdownloader" width="300"/>
</div>

# 🐺 vdownloader

تنزيل فيديوهات YouTube بجودة عالية - تطبيق ويب + تطبيق موبايل (Capacitor) + خادم Node.js

## 🌟 المميزات

- **تنزيل الفيديو** بجودات متعددة (1080p, 720p, 480p, audio only)
- **واجهة ويب** (Flask) للاستخدام من المتصفح
- **تطبيق موبايل** (Capacitor) لنظامي Android و iOS
- **خادم Node.js** سريع يعمل محلياً على الهاتف (عبر Termux)
- **دعم البروكسي** للاتصال عبر VPN/Proxy
- **تصديم داكن** أنيق وعصري

## 📁 هيكل المشروع

```
vdownloader/
├── mobile-app/               # تطبيق Capacitor (Android/iOS)
│   ├── www/                  # واجهة Vanilla JS
│   │   ├── index.html
│   │   ├── app.js
│   │   └── styles.css
│   ├── android/              # مشروع Android الأصلي
│   ├── capacitor.config.json # إعدادات Capacitor
│   └── package.json          # تبعيات npm
│
├── server/                   # خادم Node.js (Express + ytdl-core)
│   ├── server.js             # نقطة الدخول
│   └── package.json
│
├── web_app/                  # تطبيق ويب Flask (قديم)
│   ├── app.py
│   └── static/
│       ├── index.html
│       └── theme.css
│
└── README.md
```

## 🚀 التشغيل

### تطبيق الويب (Flask)

```bash
cd web_app
pip install -r ../requirements.txt
python app.py
```

### الخادم (Node.js) - للاستخدام مع تطبيق الموبايل

```bash
cd server
npm install
node server.js
```

### تطبيق الموبايل (Capacitor)

```bash
cd mobile-app
npm install
npx cap sync android
npx cap open android
```

## 📱 الاستخدام على الهاتف

1. افتح **Termux** على Android
2. شغل خادم Node.js:
   ```bash
   cd server
   node server.js
   ```
3. افتح تطبيق vdownloader - سيتصل تلقائياً بـ `localhost:3000`

## 🔧 التقنيات المستخدمة

| التقنية | الاستخدام |
|---------|-----------|
| **Capacitor** | تطبيق الموبايل (Android/iOS) |
| **Node.js + Express** | خادم API للتنزيل |
| **ytdl-core** | تنزيل فيديوهات YouTube |
| **Vanilla JS** | واجهة المستخدم |
| **Flask (قديم)** | تطبيق الويب الأصلي |

## 📄 الترخيص

MIT License
