from setuptools import setup

APP = ['main.py']
DATA_FILES = ['logo_g.png', 'secret.key', 'accounts.json', 'address_book.json']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'logo_g.icns',
    'packages': ['requests', 'cryptography', 'ttkbootstrap'],
    'includes': ['tkinter'],
    'plist': {
        'CFBundleName': 'BYBIT GShift',
        'CFBundleDisplayName': 'BYBIT GShift',
        'CFBundleIdentifier': 'com.gorchillca.bybitgshift',
        'CFBundleVersion': '0.1.3.1',
        'CFBundleShortVersionString': '0.1.3.1',
        'NSHighResolutionCapable': True
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
