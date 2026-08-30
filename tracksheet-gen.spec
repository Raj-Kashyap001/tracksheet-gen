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
    excludes=['gi', 'gi.repository', 'Gtk', 'Adw', 'Gio', 'GLib'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tracksheet-gen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tracksheet-gen',
)
