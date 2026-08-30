# -*- mode: python ; coding: utf-8 -*-
import sys

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

# On Linux: remove bundled GTK/WebKit shared libs (use system ones)
if sys.platform != 'win32':
    exclude_libs = ['libwebkit', 'libjavascriptcoregtk', 'libgtk-3', 'libgdk-3',
                    'libpango-1.0', 'libcairo', 'libharfbuzz', 'libsecret',
                    'libgio-2.0', 'libgobject-2.0', 'libglib-2.0']
    a.binaries = [b for b in a.binaries if not any(ex in b[0] for ex in exclude_libs)]

pyz = PYZ(a.pure)

if sys.platform == 'win32':
    exe = EXE(
        pyz, a.scripts, a.binaries, a.datas, [],
        name='tracksheet-gen',
        debug=False, bootloader_ignore_signals=False,
        strip=False, upx=True, console=False,
        icon='assets/icon.ico' if __import__('os').path.exists('assets/icon.ico') else None,
    )
else:
    exe = EXE(
        pyz, a.scripts, a.binaries, a.datas, [],
        name='tracksheet-gen',
        debug=False, bootloader_ignore_signals=False,
        strip=False, upx=True, console=True,
    )
