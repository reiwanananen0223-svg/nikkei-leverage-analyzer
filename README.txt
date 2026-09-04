[app]
title = Nikkei Leverage Analyzer
package.name = nikkei_analyzer
package.domain = org.nikkei.analyzer

source.dir = .
source.include_exts = py,png,jpg,kv

version = 1.0.0
requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = master
p4a.commit = 957a3e5

[buildozer]
log_level = 2
warn_on_root = 1
