# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['qme.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'dns.resolver',
        'dns.rdtypes',
        'dns.rdtypes.ANY',
        'dns.rdtypes.IN',
        'dns.rdtypes.IN.A',
        'dns.rdtypes.IN.AAAA',
        'textual.widgets',
        'textual.widgets._tab_pane',
        'textual.containers',
        'textual.app',
        'textual.binding',
        'textual.css',
        'textual.geometry',
        'textual.reactive',
        'textual.timer',
        'textual.widget',
        'textual.dom',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='qme',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
