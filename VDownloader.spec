# -*- mode: python ; coding: utf-8 -*-

import os
import glob

project_root = os.path.abspath('VDownloader')
ffmpeg_bin = r'C:\ffmpeg\bin'

a = Analysis(
    ['VDownloader/main.py'],
    pathex=[
        project_root,
        os.path.dirname(project_root),
    ],
    binaries=[
        (os.path.join(ffmpeg_bin, 'ffmpeg.exe'), 'ffmpeg'),
        (os.path.join(ffmpeg_bin, 'ffprobe.exe'), 'ffmpeg'),
    ] + [
        (os.path.join(ffmpeg_bin, f), 'ffmpeg')
        for f in os.listdir(ffmpeg_bin)
        if f.endswith('.dll')
    ],
    datas=[
        (os.path.join(project_root, 'gui'), 'gui'),
        (os.path.join(project_root, 'core'), 'core'),
        (os.path.join(project_root, 'utils'), 'utils'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'yt_dlp',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='VDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)