# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['candymain.py'],
             pathex=['/Users/jeremiegarcia/Documents/dev/candyfly/Candyfly'],
             binaries=[],
             datas=[('../README.md', '.'),
                    ('presets', 'presets'),
                    ('img', 'img'),
                    ('sounds', 'sounds')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

import sys
# Generate an executable file for windows / linux
if sys.platform == 'win32' or sys.platform == 'win64' or sys.platform == 'linux':
    exe = EXE(pyz,
            a.scripts,
            a.binaries,
            a.zipfiles,
            a.datas,
            name='CandyFly',
            debug=False,
            strip=False,
            upx=True,
            runtime_tmpdir=None,
            console=False,
            icon='img/candy.ico')

# Generate an executable file for OSX
if sys.platform == 'darwin':
    exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='CandyFly',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='img/candy.icns')

# Generate an executable file for OSX (APP)
if sys.platform == 'darwin':
    app = BUNDLE(exe,
             name='CandyFly.app',
             icon='img/candy.icns',
             info_plist={
                  'NSHighResolutionCapable': 'True'
                },
             bundle_identifier=None)
