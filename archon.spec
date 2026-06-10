# -*- mode: python ; coding: utf-8 -*-
# ──────────────────────────────────────────────────────────────────────────────
#  Archon — Spec PyInstaller  (v3 — corrige ModuleNotFoundError: xml)
#
#  • uac_admin=False  → ZERO prompt de admin
#  • console=False    → sem terminal preto
#  • xml e xmlrpc removidos dos excludes (openpyxl depende de xml.etree)
#
#  pip install --upgrade openpyxl   (antes de compilar)
#  pyinstaller archon.spec --noconfirm
# ──────────────────────────────────────────────────────────────────────────────

import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')


def maybe(src, dst):
    return [(src, dst)] if os.path.exists(src) else []


project_datas = [
    *maybe('archon_icon.ico', '.'),
    *maybe('archon_icon.png', '.'),
    *maybe('styles/theme_premium.json', 'styles'),
    *maybe('theme_premium.json',        'styles'),
    *( [('assets', 'assets')] if os.path.isdir('assets') else [] ),
    *maybe('template.xlsx', '.'),
]


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=ctk_binaries,
    datas=[
        *ctk_datas,
        *project_datas,
    ],
    hiddenimports=[
        *ctk_hiddenimports,

        # Pillow
        'PIL', 'PIL._tkinter_finder', 'PIL.Image', 'PIL.ImageDraw',
        'PIL.ImageTk', 'PIL.ImageFont', 'PIL.IcoImagePlugin',

        # System tray
        'pystray', 'pystray._win32',

        # openpyxl + dependências completas
        'openpyxl',
        'openpyxl.cell', 'openpyxl.cell.cell',
        'openpyxl.styles', 'openpyxl.styles.alignment',
        'openpyxl.styles.differential',
        'openpyxl.comments',
        'openpyxl.descriptors', 'openpyxl.descriptors.sequence',
        'openpyxl.workbook', 'openpyxl.workbook.child',
        'openpyxl.worksheet', 'openpyxl.worksheet.worksheet',
        'openpyxl.utils', 'openpyxl.utils.datetime',
        'openpyxl.xml', 'openpyxl.xml.functions',

        # xml — usado pelo openpyxl (estava nos excludes por engano)
        'xml', 'xml.etree', 'xml.etree.ElementTree',
        'xml.etree.cElementTree',

        # Numpy (dependência interna do openpyxl)
        'numpy', 'numpy.core', 'numpy.core._multiarray_umath',

        # Tkinter
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.filedialog',

        # Módulos próprios
        'database', 'database.database',
        'modules', 'modules.layout', 'modules.dashboard',
        'modules.clientes', 'modules.processos', 'modules.financeiro',
        'modules.calendario', 'modules.estrategias',
        'utils', 'colors',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Apenas o que certamente não é usado
        'matplotlib', 'scipy', 'pandas',
        'jupyter', 'IPython',
        'unittest', 'distutils',
        '_pytest', 'pytest',
        'docutils', 'sphinx',
        # email/http/urllib removidos também — podem ser puxados por deps internas
    ],
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
    name='Archon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='archon_icon.ico',
    uac_admin=False,        # ← ZERO prompt de admin
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['vcruntime140.dll', 'python3*.dll'],
    name='Archon',
)
