# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    # 修正ポイント: templatesフォルダを丸ごと同梱する
    datas=[('templates', 'templates')],
    # 修正ポイント: インポートエラーを防ぐための明示的な指定
    hiddenimports=['engineio.async_drivers.threading', 'eventlet', 'flask_socketio'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    # 修正ポイント: 実行ファイル名を変更（任意）
    name='RemoteController',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    # 修正ポイント: QRコードを表示するためにTrueにする
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app.ico'],
)