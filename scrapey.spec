# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add data files
data_files = [
    ('scrapey/*.ini', 'scrapey'),
    ('scrapey/gui', 'scrapey/gui'),
    ('LICENSE', '.'),
    ('README.md', '.'),
    ('resources/scrapey.icns', '.')
]

a = Analysis(
    ['scrapey/main.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'pdf2image',
        'pytesseract',
        'easyocr'
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
    [],
    exclude_binaries=True,
    name='scrapey',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='scrapey',
)

app = BUNDLE(
    coll,
    name='scrapey.app',
    icon='resources/scrapey.icns',
    info_plist={
        'CFBundleName': 'scrapey',
        'CFBundleDisplayName': 'Scrapey',
        'CFBundleGetInfoString': 'Text extraction tool',
        'CFBundleIdentifier': 'com.scrapey.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'CFBundleIconFile': 'scrapey.icns',
    },
) 