# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the CareerForge AI backend sidecar.
# Uses relative paths (SPECPATH) so it works in CI on any OS.
from PyInstaller.utils.hooks import collect_submodules, collect_all

datas = [
    (SPECPATH + '/templates', 'templates'),
    (SPECPATH + '/prompts', 'prompts'),
]
binaries = []
hiddenimports = [
    'aiosqlite',
    'sqlalchemy.ext.asyncio',
    'sqlalchemy.dialects.sqlite.aiosqlite',
    'fitz',
    'app.main',
    'app.config.settings',
    'app.db.base',
    'app.services.ai.orchestrator',
]
hiddenimports += collect_submodules('app')
hiddenimports += collect_submodules('uvicorn')

# Heavy native packages must be fully collected so they run from a frozen bundle.
for pkg in ('sentence_transformers', 'lancedb', 'uvicorn', 'aiosqlite', 'numpy', 'pyarrow', 'keybert'):
    try:
        tmp_ret = collect_all(pkg)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception:
        pass

a = Analysis(
    [SPECPATH + '/app/main.py'],
    pathex=[SPECPATH],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='careerforge-backend',
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
