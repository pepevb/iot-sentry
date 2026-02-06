"""
IoT Sentry - Geolocalizador de IPs

Geolocalización offline usando base de datos GeoLite2
"""

import os
from typing import Optional, Dict
import geoip2.database
from functools import lru_cache


class GeoLocator:
    """Geolocalizador de direcciones IP"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializar geolocalizador

        Args:
            db_path: Ruta a GeoLite2-City.mmdb (None = ubicación por defecto)
        """
        if db_path is None:
            # Buscar en ubicación por defecto
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(project_root, 'shared', 'databases', 'GeoLite2-City.mmdb')

        self.db_path = db_path
        self.reader = None

        # Intentar cargar base de datos
        self._load_database()

    def _load_database(self):
        """
        Cargar base de datos GeoLite2
        """
        if not os.path.exists(self.db_path):
            print(f"⚠️  Base de datos GeoLite2 no encontrada en: {self.db_path}")
            print("   Ejecuta: ./scripts/download-geodata.sh")
            return

        try:
            self.reader = geoip2.database.Reader(self.db_path)
            print(f"✅ Base de datos GeoLite2 cargada")
        except Exception as e:
            print(f"❌ Error cargando GeoLite2: {e}")

    @lru_cache(maxsize=1024)
    def geolocate(self, ip_address: str) -> Optional[Dict]:
        """
        Geolocalizar dirección IP

        Args:
            ip_address: Dirección IP a geolocalizar

        Returns:
            Dict con información geográfica o None si no se encuentra:
            {
                'country': 'United States',
                'country_code': 'US',
                'city': 'Mountain View',
                'latitude': 37.386,
                'longitude': -122.0838,
                'continent': 'North America'
            }
        """
        if not self.reader:
            return None

        # Filtrar IPs privadas
        if self._is_private_ip(ip_address):
            return {
                'country': 'Local Network',
                'country_code': 'LAN',
                'city': 'Private',
                'latitude': None,
                'longitude': None,
                'continent': 'Local'
            }

        try:
            response = self.reader.city(ip_address)

            return {
                'country': response.country.name or 'Unknown',
                'country_code': response.country.iso_code or '??',
                'city': response.city.name or 'Unknown',
                'latitude': response.location.latitude,
                'longitude': response.location.longitude,
                'continent': response.continent.name or 'Unknown'
            }

        except geoip2.errors.AddressNotFoundError:
            # IP no encontrada en base de datos
            return {
                'country': 'Unknown',
                'country_code': '??',
                'city': 'Unknown',
                'latitude': None,
                'longitude': None,
                'continent': 'Unknown'
            }
        except Exception as e:
            print(f"⚠️  Error geolocalizando {ip_address}: {e}")
            return None

    def _is_private_ip(self, ip: str) -> bool:
        """
        Verificar si una IP es privada/local

        Args:
            ip: Dirección IP

        Returns:
            True si es IP privada
        """
        # Rangos privados
        private_ranges = [
            '10.',           # 10.0.0.0/8
            '172.16.', '172.17.', '172.18.', '172.19.',  # 172.16.0.0/12
            '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.',
            '172.28.', '172.29.', '172.30.', '172.31.',
            '192.168.',      # 192.168.0.0/16
            '127.',          # Loopback
            'localhost'
        ]

        return any(ip.startswith(prefix) for prefix in private_ranges)

    def close(self):
        """
        Cerrar conexión a base de datos
        """
        if self.reader:
            self.reader.close()
            print("✅ GeoIP database cerrada")


def main():
    """
    Función principal para testing standalone
    """
    print("🛡️  IoT Sentry - GeoLocator Test")
    print("=" * 50)
    print()

    locator = GeoLocator()

    # Test IPs
    test_ips = [
        '8.8.8.8',           # Google DNS
        '1.1.1.1',           # Cloudflare DNS
        '52.84.150.20',      # Amazon AWS
        '192.168.1.1',       # IP privada
        '142.250.185.46',    # Google
    ]

    print("🧪 Testing geolocalización:\n")

    for ip in test_ips:
        result = locator.geolocate(ip)
        if result:
            print(f"📍 {ip}")
            print(f"   País: {result['country']} ({result['country_code']})")
            print(f"   Ciudad: {result['city']}")
            if result['latitude'] and result['longitude']:
                print(f"   Coords: {result['latitude']}, {result['longitude']}")
            print()

    locator.close()
    print("✨ Test completado!")


if __name__ == "__main__":
    main()
