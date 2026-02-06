"""
IoT Sentry - Scanner de Red

Descubre dispositivos en la red local mediante escaneo ARP
"""

import socket
import struct
from datetime import datetime
from typing import List, Dict, Optional
from scapy.all import ARP, Ether, srp, conf
import netifaces


class NetworkScanner:
    """Scanner de red para descubrir dispositivos IoT"""

    def __init__(self):
        # Desactivar verbose de Scapy
        conf.verb = 0

    def get_local_network_info(self) -> Dict[str, str]:
        """
        Obtener información de la red local

        Returns:
            Dict con 'ip', 'netmask' y 'network'
        """
        try:
            # Obtener interfaz de red activa (excluir loopback)
            gateways = netifaces.gateways()
            default_interface = gateways['default'][netifaces.AF_INET][1]

            # Obtener IP y netmask de la interfaz
            addrs = netifaces.ifaddresses(default_interface)
            ipv4_info = addrs[netifaces.AF_INET][0]

            ip = ipv4_info['addr']
            netmask = ipv4_info['netmask']

            # Calcular red en formato CIDR
            network = self._calculate_network_cidr(ip, netmask)

            return {
                'ip': ip,
                'netmask': netmask,
                'network': network,
                'interface': default_interface
            }
        except Exception as e:
            print(f"❌ Error obteniendo información de red: {e}")
            # Fallback a red común
            return {
                'ip': '192.168.1.1',
                'netmask': '255.255.255.0',
                'network': '192.168.1.0/24',
                'interface': 'unknown'
            }

    def _calculate_network_cidr(self, ip: str, netmask: str) -> str:
        """
        Calcular dirección de red en formato CIDR

        Args:
            ip: Dirección IP (ej. '192.168.1.100')
            netmask: Máscara de red (ej. '255.255.255.0')

        Returns:
            Red en formato CIDR (ej. '192.168.1.0/24')
        """
        # Convertir IP y netmask a enteros
        ip_int = struct.unpack('!I', socket.inet_aton(ip))[0]
        netmask_int = struct.unpack('!I', socket.inet_aton(netmask))[0]

        # Calcular dirección de red
        network_int = ip_int & netmask_int

        # Convertir de vuelta a string
        network = socket.inet_ntoa(struct.pack('!I', network_int))

        # Calcular CIDR (contar bits en 1 de la netmask)
        cidr = bin(netmask_int).count('1')

        return f"{network}/{cidr}"

    def scan_network(self, network: Optional[str] = None, timeout: int = 3) -> List[Dict]:
        """
        Escanear red local en busca de dispositivos activos

        Args:
            network: Red a escanear en formato CIDR (ej. '192.168.1.0/24').
                    Si es None, se detecta automáticamente.
            timeout: Timeout en segundos para cada request ARP

        Returns:
            Lista de diccionarios con información de dispositivos:
            [
                {
                    'ip': '192.168.1.100',
                    'mac': 'AA:BB:CC:DD:EE:FF',
                    'hostname': 'my-camera',
                    'timestamp': datetime.utcnow()
                },
                ...
            ]
        """
        # Auto-detectar red si no se especifica
        if network is None:
            net_info = self.get_local_network_info()
            network = net_info['network']
            print(f"🔍 Escaneando red: {network} (interfaz: {net_info['interface']})")
        else:
            print(f"🔍 Escaneando red: {network}")

        # Crear paquete ARP request
        arp = ARP(pdst=network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast
        packet = ether / arp

        # Enviar y recibir
        print("📡 Enviando ARP requests...")
        result = srp(packet, timeout=timeout, verbose=False)[0]

        # Procesar resultados
        devices = []
        for sent, received in result:
            device = {
                'ip': received.psrc,
                'mac': received.hwsrc.upper(),
                'hostname': self._resolve_hostname(received.psrc),
                'timestamp': datetime.utcnow()
            }
            devices.append(device)

        print(f"✅ Encontrados {len(devices)} dispositivos")
        return devices

    def _resolve_hostname(self, ip: str) -> Optional[str]:
        """
        Intentar resolver hostname de una IP

        Args:
            ip: Dirección IP

        Returns:
            Hostname o None si no se puede resolver
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except (socket.herror, socket.gaierror):
            return None

    def get_gateway(self) -> Optional[str]:
        """
        Obtener la IP del gateway (router)

        Returns:
            IP del gateway o None
        """
        try:
            gateways = netifaces.gateways()
            return gateways['default'][netifaces.AF_INET][0]
        except Exception:
            return None


def main():
    """
    Función principal para testing standalone
    """
    print("🛡️  IoT Sentry - Network Scanner")
    print("=" * 50)
    print()

    scanner = NetworkScanner()

    # Obtener info de red
    net_info = scanner.get_local_network_info()
    print(f"🌐 Red local detectada:")
    print(f"   IP: {net_info['ip']}")
    print(f"   Netmask: {net_info['netmask']}")
    print(f"   Network: {net_info['network']}")
    print(f"   Interface: {net_info['interface']}")
    print()

    # Escanear red
    devices = scanner.scan_network()

    # Mostrar resultados
    print()
    print(f"📱 Dispositivos encontrados ({len(devices)}):")
    print("-" * 50)
    for device in devices:
        hostname = device['hostname'] or 'N/A'
        print(f"  • {device['ip']:15} | {device['mac']:17} | {hostname}")

    print()
    print("✨ Escaneo completado!")


if __name__ == "__main__":
    main()
