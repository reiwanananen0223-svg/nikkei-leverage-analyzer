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

# Network access for market-data retrieval
android.permissions = INTERNET

# Keep the first build simple.
android.api = 35
android.minapi = 23
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
