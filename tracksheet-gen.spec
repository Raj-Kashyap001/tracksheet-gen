# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['gen_tracksheet_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/index.html', 'assets'), ('assets/icon.png', 'assets')],
    hiddenimports=['gen_tracksheet'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Remove bundled GTK/WebKit shared libs — use system ones at runtime
exclude_libs = ['libwebkit', 'libjavascriptcoregtk', 'libgtk-3', 'libgdk-3',
                'libpango-1', 'libcairo', 'libharfbuzz', 'libsecret']
a.binaries = [b for b in a.binaries if not any(ex in b[0] for ex in exclude_libs)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='tracksheet-gen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
