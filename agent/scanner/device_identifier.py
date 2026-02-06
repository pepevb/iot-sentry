"""
IoT Sentry - Identificador de Dispositivos

Identifica fabricantes y tipos de dispositivos basándose en MAC address (OUI) y heurísticas
"""

import os
import re
from typing import Optional, Dict


class DeviceIdentifier:
    """Identificador de dispositivos IoT"""

    def __init__(self, oui_file: Optional[str] = None):
        """
        Inicializar identificador

        Args:
            oui_file: Ruta al archivo OUI de IEEE. Si es None, se busca en shared/databases/
        """
        if oui_file is None:
            # Buscar archivo OUI en ubicación por defecto
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            oui_file = os.path.join(project_root, 'shared', 'databases', 'oui.txt')

        self.oui_file = oui_file
        self.oui_cache = {}
        self._load_oui_database()

        # Mapa de fabricantes conocidos de IoT a tipos de dispositivos
        self.vendor_to_type = {
            'Amazon': 'smart_speaker',
            'Google': 'smart_speaker',
            'Apple': 'smart_speaker',
            'Sonos': 'smart_speaker',
            'Philips': 'smart_bulb',
            'LIFX': 'smart_bulb',
            'TP-Link': 'smart_plug',
            'Wyze': 'camera',
            'Ring': 'doorbell',
            'Nest': 'thermostat',
            'Ecobee': 'thermostat',
            'Samsung': 'smart_tv',
            'LG': 'smart_tv',
            'Sony': 'smart_tv',
            'Xiaomi': 'various',
            'Tuya': 'various',
        }

    def _load_oui_database(self):
        """
        Cargar base de datos OUI en memoria (caché)

        Formato del archivo OUI:
        00-00-00   (hex)    XEROX CORPORATION
        00-00-01   (hex)    XEROX CORPORATION
        ...
        """
        if not os.path.exists(self.oui_file):
            print(f"⚠️  Advertencia: Archivo OUI no encontrado en {self.oui_file}")
            print("   Ejecuta: ./scripts/download-geodata.sh")
            return

        print(f"📚 Cargando base de datos OUI...")
        try:
            with open(self.oui_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Buscar líneas con formato: XX-XX-XX   (hex)    VENDOR NAME
                    match = re.match(r'([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+\(hex\)\s+(.+)', line)
                    if match:
                        oui = match.group(1).replace('-', ':')
                        vendor = match.group(2).strip()
                        self.oui_cache[oui] = vendor

            print(f"✅ Cargados {len(self.oui_cache)} OUIs")
        except Exception as e:
            print(f"❌ Error cargando OUI database: {e}")

    def get_vendor(self, mac_address: str) -> str:
        """
        Obtener fabricante desde MAC address

        Args:
            mac_address: Dirección MAC (formato: 'AA:BB:CC:DD:EE:FF')

        Returns:
            Nombre del fabricante o 'Unknown'
        """
        # Extraer OUI (primeros 3 octetos)
        oui = ':'.join(mac_address.upper().split(':')[:3])

        # Buscar en caché
        vendor = self.oui_cache.get(oui, 'Unknown')

        return vendor

    def identify_device_type(self, vendor: str, hostname: Optional[str] = None) -> str:
        """
        Identificar tipo de dispositivo basándose en fabricante y hostname

        Args:
            vendor: Fabricante del dispositivo
            hostname: Hostname (opcional, puede dar pistas adicionales)

        Returns:
            Tipo de dispositivo: 'camera', 'speaker', 'bulb', 'tv', 'router', 'unknown'
        """
        # Normalizar vendor
        vendor_lower = vendor.lower()

        # Heurísticas basadas en fabricante
        for known_vendor, device_type in self.vendor_to_type.items():
            if known_vendor.lower() in vendor_lower:
                return device_type

        # Heurísticas basadas en hostname
        if hostname:
            hostname_lower = hostname.lower()

            if any(keyword in hostname_lower for keyword in ['camera', 'cam', 'ipcam']):
                return 'camera'
            elif any(keyword in hostname_lower for keyword in ['speaker', 'echo', 'alexa', 'google-home']):
                return 'smart_speaker'
            elif any(keyword in hostname_lower for keyword in ['bulb', 'light', 'lamp']):
                return 'smart_bulb'
            elif any(keyword in hostname_lower for keyword in ['tv', 'television']):
                return 'smart_tv'
            elif any(keyword in hostname_lower for keyword in ['router', 'gateway', 'modem']):
                return 'router'
            elif any(keyword in hostname_lower for keyword in ['plug', 'switch', 'outlet']):
                return 'smart_plug'
            elif any(keyword in hostname_lower for keyword in ['thermostat', 'nest']):
                return 'thermostat'
            elif any(keyword in hostname_lower for keyword in ['doorbell', 'ring']):
                return 'doorbell'

        # Por defecto
        return 'unknown'

    def identify_device(self, mac_address: str, hostname: Optional[str] = None) -> Dict[str, str]:
        """
        Identificar dispositivo completo

        Args:
            mac_address: Dirección MAC
            hostname: Hostname opcional

        Returns:
            Diccionario con 'vendor' y 'device_type'
        """
        vendor = self.get_vendor(mac_address)
        device_type = self.identify_device_type(vendor, hostname)

        return {
            'vendor': vendor,
            'device_type': device_type
        }


def main():
    """
    Función principal para testing standalone
    """
    print("🛡️  IoT Sentry - Device Identifier")
    print("=" * 50)
    print()

    identifier = DeviceIdentifier()

    # Test cases
    test_devices = [
        {'mac': '00:1A:11:FF:FF:FF', 'hostname': 'google-home'},
        {'mac': 'F0:81:73:FF:FF:FF', 'hostname': 'wyze-cam-v3'},
        {'mac': '00:17:88:FF:FF:FF', 'hostname': 'philips-hue'},
        {'mac': 'B4:E6:2D:FF:FF:FF', 'hostname': None},
    ]

    print("🧪 Testing device identification:")
    print("-" * 50)
    for device in test_devices:
        result = identifier.identify_device(device['mac'], device['hostname'])
        hostname = device['hostname'] or 'N/A'
        print(f"MAC: {device['mac']}")
        print(f"  Hostname: {hostname}")
        print(f"  Vendor: {result['vendor']}")
        print(f"  Type: {result['device_type']}")
        print()

    print("✨ Testing completado!")


if __name__ == "__main__":
    main()
