[app]

title = VDownloader
package.name = vdownloader
package.domain = org.vdownloader

source.dir = ..
source.include_dirs = gui,core,utils
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,yt-dlp,requests,jnius,plyer

orientation = portrait

osx.python_version = 3
osx.kivy_version = 2.3.0

fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 21
android.minapi = 21
android.archs = arm64-v8a,armeabi-v7a

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_target = 2.14

android.sdk_location = /home/runner/android-sdk
android.ndk_api = 21
android.allow_debug_apis = 1

[buildozer]

log_level = 2

warn_on_root = 1

build_dir = ./.buildozer
bin_dir = ./bin