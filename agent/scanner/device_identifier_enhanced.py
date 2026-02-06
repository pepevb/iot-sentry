"""
IoT Sentry - Identificador de Dispositivos MEJORADO

Identifica fabricantes y tipos de dispositivos con más detalle
"""

import os
import re
from typing import Optional, Dict


class EnhancedDeviceIdentifier:
    """Identificador mejorado de dispositivos IoT"""

    def __init__(self, oui_file: Optional[str] = None):
        """
        Inicializar identificador

        Args:
            oui_file: Ruta al archivo OUI de IEEE
        """
        if oui_file is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            oui_file = os.path.join(project_root, 'shared', 'databases', 'oui.txt')

        self.oui_file = oui_file
        self.oui_cache = {}
        self._load_oui_database()

        # Mapa EXTENDIDO de fabricantes a tipos de dispositivos
        self.vendor_patterns = {
            # Móviles
            'mobile': [
                'Apple', 'Samsung', 'Huawei', 'Xiaomi', 'OnePlus', 'Oppo', 'Vivo',
                'Motorola', 'LG Electronics', 'Google', 'HTC', 'Nokia', 'Sony Mobile'
            ],

            # PCs y Laptops
            'computer': [
                'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'MSI', 'Toshiba',
                'Intel Corporate', 'ASUSTek', 'Hewlett Packard'
            ],

            # IoT - Cámaras
            'camera': [
                'Wyze', 'Ring', 'Arlo', 'Nest', 'Blink', 'Reolink', 'Amcrest',
                'Hikvision', 'Dahua', 'Axis', 'Vivotek', 'Foscam', 'Yi'
            ],

            # IoT - Asistentes/Speakers
            'smart_speaker': [
                'Amazon', 'Google', 'Sonos', 'Bose', 'Apple', 'Harman',
                'JBL', 'Ultimate Ears'
            ],

            # IoT - Iluminación
            'smart_bulb': [
                'Philips', 'LIFX', 'TP-Link', 'Sengled', 'Wyze', 'GE Lighting',
                'Yeelight', 'Nanoleaf'
            ],

            # IoT - Enchufes
            'smart_plug': [
                'TP-Link', 'Wemo', 'Kasa', 'Meross', 'Gosund', 'Teckin'
            ],

            # IoT - Termostatos
            'thermostat': [
                'Nest', 'Ecobee', 'Honeywell', 'Emerson'
            ],

            # IoT - Timbres
            'doorbell': [
                'Ring', 'Nest', 'Arlo', 'Eufy', 'Wyze'
            ],

            # TVs
            'smart_tv': [
                'Samsung', 'LG', 'Sony', 'Vizio', 'TCL', 'Hisense', 'Sharp',
                'Panasonic', 'Toshiba'
            ],

            # Consolas de videojuegos
            'game_console': [
                'Sony', 'Microsoft', 'Nintendo', 'Valve'
            ],

            # Routers y Networking
            'router': [
                'TP-Link', 'Netgear', 'Asus', 'Linksys', 'D-Link', 'Ubiquiti',
                'Cisco', 'MikroTik', 'Arris', 'Motorola'
            ],

            # Electrodomésticos inteligentes
            'smart_appliance': [
                'Samsung SmartThings', 'LG ThinQ', 'Whirlpool', 'GE Appliances',
                'Bosch', 'iRobot', 'Roborock', 'Ecovacs', 'Shark', 'Dyson'
            ],

            # Wearables
            'wearable': [
                'Fitbit', 'Garmin', 'Fossil', 'Withings', 'Amazfit'
            ],

            # Tablets
            'tablet': [
                'Apple iPad', 'Samsung Galaxy Tab', 'Amazon Fire'
            ],

            # Impresoras
            'printer': [
                'HP', 'Canon', 'Epson', 'Brother', 'Lexmark', 'Xerox'
            ],

            # NAS / Almacenamiento
            'nas': [
                'Synology', 'QNAP', 'Western Digital', 'Seagate'
            ],

            # Media Streaming
            'media_streamer': [
                'Roku', 'Chromecast', 'Apple TV', 'Amazon Fire TV', 'Nvidia Shield'
            ]
        }

        # Patrones de hostname (más específicos)
        self.hostname_patterns = {
            # Móviles
            'mobile': [
                r'iphone', r'android', r'galaxy[-\s]?s\d+', r'pixel[-\s]?\d+',
                r'oneplus', r'xiaomi', r'redmi', r'mobile', r'phone'
            ],

            # PCs
            'computer': [
                r'desktop', r'laptop', r'pc[-\s]', r'workstation', r'macbook',
                r'imac', r'thinkpad', r'latitude', r'inspiron'
            ],

            # Cámaras
            'camera': [
                r'camera', r'cam[-\s]', r'ipcam', r'wyze[-\s]?cam', r'ring[-\s]?cam',
                r'arlo', r'nest[-\s]?cam', r'blink'
            ],

            # Asistentes
            'smart_speaker': [
                r'echo', r'alexa', r'google[-\s]?home', r'nest[-\s]?hub',
                r'homepod', r'sonos'
            ],

            # Iluminación
            'smart_bulb': [
                r'bulb', r'light', r'lamp', r'hue[-\s]?', r'lifx'
            ],

            # Enchufes
            'smart_plug': [
                r'plug', r'switch', r'outlet', r'socket', r'kasa'
            ],

            # Termostatos
            'thermostat': [
                r'thermostat', r'nest[-\s]?thermo', r'ecobee'
            ],

            # Timbres
            'doorbell': [
                r'doorbell', r'ring[-\s]?door', r'bell'
            ],

            # TVs
            'smart_tv': [
                r'tv', r'television', r'samsung[-\s]?tv', r'lg[-\s]?tv', r'roku[-\s]?tv'
            ],

            # Consolas
            'game_console': [
                r'playstation', r'ps[345]', r'xbox', r'nintendo', r'switch',
                r'steam[-\s]?deck'
            ],

            # Routers
            'router': [
                r'router', r'gateway', r'modem', r'access[-\s]?point', r'ap[-\s]'
            ],

            # Aspiradoras/Robots
            'smart_appliance': [
                r'roomba', r'vacuum', r'roborock', r'dyson', r'robot',
                r'fridge', r'washer', r'dryer', r'oven', r'dishwasher'
            ],

            # Wearables
            'wearable': [
                r'watch', r'fitbit', r'band', r'tracker'
            ],

            # Tablets
            'tablet': [
                r'ipad', r'tablet', r'kindle[-\s]?fire'
            ],

            # Impresoras
            'printer': [
                r'printer', r'print', r'hp[-\s]?laserjet', r'epson', r'canon'
            ],

            # NAS
            'nas': [
                r'nas', r'synology', r'qnap', r'diskstation'
            ],

            # Streamers
            'media_streamer': [
                r'chromecast', r'roku', r'firetv', r'appletv', r'nvidia[-\s]?shield'
            ]
        }

    def _load_oui_database(self):
        """Cargar base de datos OUI en memoria"""
        if not os.path.exists(self.oui_file):
            print(f"⚠️  OUI database no encontrado")
            return

        try:
            with open(self.oui_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match = re.match(r'([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+\(hex\)\s+(.+)', line)
                    if match:
                        oui = match.group(1).replace('-', ':')
                        vendor = match.group(2).strip()
                        self.oui_cache[oui] = vendor
            print(f"✅ Cargados {len(self.oui_cache)} OUIs")
        except Exception as e:
            print(f"❌ Error cargando OUI: {e}")

    def get_vendor(self, mac_address: str) -> str:
        """Obtener fabricante desde MAC address"""
        oui = ':'.join(mac_address.upper().split(':')[:3])
        return self.oui_cache.get(oui, 'Unknown')

    def identify_device_type(self, vendor: str, hostname: Optional[str] = None) -> str:
        """
        Identificar tipo de dispositivo (MEJORADO)

        Returns:
            Tipo de dispositivo detallado
        """
        vendor_lower = vendor.lower()

        # 1. Verificar por fabricante
        for device_type, vendors in self.vendor_patterns.items():
            for known_vendor in vendors:
                if known_vendor.lower() in vendor_lower:
                    # Refinamiento adicional por hostname si está disponible
                    if hostname:
                        refined_type = self._refine_by_hostname(hostname, device_type)
                        if refined_type != device_type:
                            return refined_type
                    return device_type

        # 2. Verificar por hostname (si no hubo match en vendor)
        if hostname:
            hostname_lower = hostname.lower()

            for device_type, patterns in self.hostname_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, hostname_lower):
                        return device_type

        # 3. Por defecto
        return 'unknown'

    def _refine_by_hostname(self, hostname: str, initial_type: str) -> str:
        """
        Refinar tipo de dispositivo usando hostname

        Útil cuando un fabricante hace múltiples tipos de dispositivos
        (ej. Samsung hace móviles, TVs, electrodomésticos)
        """
        hostname_lower = hostname.lower()

        for device_type, patterns in self.hostname_patterns.items():
            for pattern in patterns:
                if re.search(pattern, hostname_lower):
                    return device_type

        return initial_type

    def get_device_category(self, device_type: str) -> str:
        """
        Obtener categoría general del dispositivo

        Returns:
            'personal' | 'iot' | 'networking' | 'entertainment' | 'appliance'
        """
        categories = {
            'personal': ['mobile', 'computer', 'tablet', 'wearable'],
            'iot': ['camera', 'smart_speaker', 'smart_bulb', 'smart_plug',
                   'thermostat', 'doorbell'],
            'networking': ['router'],
            'entertainment': ['smart_tv', 'game_console', 'media_streamer'],
            'appliance': ['smart_appliance', 'printer', 'nas']
        }

        for category, types in categories.items():
            if device_type in types:
                return category

        return 'unknown'

    def get_device_icon(self, device_type: str) -> str:
        """
        Obtener emoji/icono para el tipo de dispositivo

        Returns:
            Emoji representativo
        """
        icons = {
            'mobile': '📱',
            'computer': '💻',
            'tablet': '📱',
            'camera': '📷',
            'smart_speaker': '🔊',
            'smart_bulb': '💡',
            'smart_plug': '🔌',
            'thermostat': '🌡️',
            'doorbell': '🔔',
            'smart_tv': '📺',
            'game_console': '🎮',
            'router': '📡',
            'smart_appliance': '🏠',
            'wearable': '⌚',
            'printer': '🖨️',
            'nas': '💾',
            'media_streamer': '📺',
            'unknown': '❓'
        }

        return icons.get(device_type, '❓')

    def identify_device(self, mac_address: str, hostname: Optional[str] = None) -> Dict[str, str]:
        """
        Identificar dispositivo completo con información extendida

        Returns:
            Dict con vendor, device_type, category, icon
        """
        vendor = self.get_vendor(mac_address)
        device_type = self.identify_device_type(vendor, hostname)
        category = self.get_device_category(device_type)
        icon = self.get_device_icon(device_type)

        return {
            'vendor': vendor,
            'device_type': device_type,
            'category': category,
            'icon': icon,
            'display_name': self._get_display_name(device_type)
        }

    def _get_display_name(self, device_type: str) -> str:
        """Obtener nombre legible para humanos"""
        display_names = {
            'mobile': 'Teléfono Móvil',
            'computer': 'Computadora',
            'tablet': 'Tablet',
            'camera': 'Cámara IP',
            'smart_speaker': 'Asistente de Voz',
            'smart_bulb': 'Bombilla Inteligente',
            'smart_plug': 'Enchufe Inteligente',
            'thermostat': 'Termostato',
            'doorbell': 'Timbre Inteligente',
            'smart_tv': 'Smart TV',
            'game_console': 'Consola de Videojuegos',
            'router': 'Router',
            'smart_appliance': 'Electrodoméstico',
            'wearable': 'Dispositivo Wearable',
            'printer': 'Impresora',
            'nas': 'Almacenamiento en Red',
            'media_streamer': 'Dispositivo de Streaming',
            'unknown': 'Desconocido'
        }

        return display_names.get(device_type, 'Desconocido')


def main():
    """Testing"""
    print("🛡️  IoT Sentry - Enhanced Device Identifier")
    print("=" * 50)

    identifier = EnhancedDeviceIdentifier()

    # Test cases
    test_devices = [
        {'mac': '00:1A:11:FF:FF:FF', 'hostname': 'google-home'},
        {'mac': 'F0:81:73:FF:FF:FF', 'hostname': 'iPhone-de-Juan'},
        {'mac': '00:17:88:FF:FF:FF', 'hostname': 'philips-hue-lamp'},
        {'mac': 'B4:E6:2D:FF:FF:FF', 'hostname': 'DESKTOP-PC'},
        {'mac': 'AA:BB:CC:DD:EE:FF', 'hostname': 'Roomba-785'},
    ]

    print("\n🧪 Testing identificación mejorada:\n")
    for device in test_devices:
        result = identifier.identify_device(device['mac'], device['hostname'])
        print(f"{result['icon']} {device['hostname']}")
        print(f"   Tipo: {result['display_name']}")
        print(f"   Categoría: {result['category']}")
        print(f"   Fabricante: {result['vendor']}")
        print()


if __name__ == "__main__":
    main()
