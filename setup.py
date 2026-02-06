"""
Setup script para empaquetar IoT Sentry como aplicación macOS
"""

from setuptools import setup

APP = ['menubar_main.py']
DATA_FILES = [
    ('assets', [
        'assets/shield.png',
        'assets/shield_alert.png',
        'assets/shield_64.png',
        'assets/shield_128.png',
        'assets/network_64.png',
        'assets/signal_64.png',
        'assets/alert_64.png',
        'assets/radar_64.png',
        'assets/network_128.png',
        'assets/signal_128.png',
        'assets/alert_128.png',
        'assets/radar_128.png',
    ]),
    ('data', []),  # Base de datos
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/shield_128.png',  # Icono de la app
    'plist': {
        'CFBundleName': 'IoT Sentry',
        'CFBundleDisplayName': 'IoT Sentry',
        'CFBundleGetInfoString': 'Auditoría de privacidad para dispositivos IoT',
        'CFBundleIdentifier': 'com.iotsentry.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2026 IoT Sentry',
        'LSUIElement': True,  # Importante: app de menu bar sin icono en Dock
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'rumps',
        'PyQt6',
        'scapy',
        'netifaces',
        'sqlalchemy',
        'geoip2',
    ],
    'includes': [
        'menubar_main',
        'core',
        'gui',
        'agent',
    ],
}

setup(
    app=APP,
    name='IoT Sentry',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
