"""
IoT Sentry - Captura de Paquetes

Captura pasiva de tráfico de red para análisis
"""

from scapy.all import sniff, IP, TCP, UDP, conf
from datetime import datetime
from typing import Callable, Optional, Set
import threading


class PacketCapture:
    """Captura de paquetes de red"""

    def __init__(self, interface: Optional[str] = None):
        """
        Inicializar capturador de paquetes

        Args:
            interface: Interfaz de red (None = auto-detectar)
        """
        self.interface = interface
        self.running = False
        self.thread = None
        self.packet_callback = None

        # Desactivar verbose de Scapy
        conf.verb = 0

        # Set de IPs a monitorear (dispositivos conocidos)
        self.monitored_ips: Set[str] = set()

    def set_monitored_devices(self, ip_addresses: list):
        """
        Configurar IPs de dispositivos a monitorear

        Args:
            ip_addresses: Lista de IPs de dispositivos IoT
        """
        self.monitored_ips = set(ip_addresses)
        print(f"📡 Monitoreando {len(self.monitored_ips)} dispositivos")

    def set_callback(self, callback: Callable):
        """
        Configurar callback para procesar paquetes capturados

        Args:
            callback: Función que recibe (src_ip, dst_ip, dst_port, protocol, size)
        """
        self.packet_callback = callback

    def _process_packet(self, packet):
        """
        Procesar paquete capturado

        Args:
            packet: Paquete Scapy
        """
        try:
            # Verificar que tenga capa IP
            if not packet.haslayer(IP):
                return

            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst

            # Solo procesar si el origen es un dispositivo monitoreado
            if src_ip not in self.monitored_ips:
                return

            # Determinar protocolo y puerto
            protocol = "OTHER"
            dst_port = None
            packet_size = len(packet)

            if packet.haslayer(TCP):
                protocol = "TCP"
                dst_port = packet[TCP].dport
            elif packet.haslayer(UDP):
                protocol = "UDP"
                dst_port = packet[UDP].dport

            # Llamar callback si está configurado
            if self.packet_callback:
                self.packet_callback(
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    dst_port=dst_port,
                    protocol=protocol,
                    size=packet_size,
                    timestamp=datetime.utcnow()
                )

        except Exception as e:
            print(f"⚠️  Error procesando paquete: {e}")

    def _capture_loop(self):
        """
        Loop de captura (ejecutado en thread separado)
        """
        try:
            print(f"🔍 Iniciando captura en interfaz: {self.interface or 'auto'}")

            # Filtro BPF para optimizar captura
            # Solo capturamos IP outbound (desde nuestra red)
            bpf_filter = "ip"

            # Iniciar captura
            sniff(
                iface=self.interface,
                filter=bpf_filter,
                prn=self._process_packet,
                store=False,  # No almacenar paquetes en memoria
                stop_filter=lambda x: not self.running
            )

        except Exception as e:
            print(f"❌ Error en captura de paquetes: {e}")
            self.running = False

    def start(self):
        """
        Iniciar captura de paquetes en background
        """
        if self.running:
            print("⚠️  Captura ya está en ejecución")
            return

        self.running = True

        # Iniciar thread de captura
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

        print("✅ Captura de paquetes iniciada")

    def stop(self):
        """
        Detener captura de paquetes
        """
        if not self.running:
            return

        print("🛑 Deteniendo captura...")
        self.running = False

        if self.thread:
            self.thread.join(timeout=2)

        print("✅ Captura detenida")

    def is_running(self) -> bool:
        """
        Verificar si la captura está activa

        Returns:
            True si está capturando
        """
        return self.running


def main():
    """
    Función principal para testing standalone
    """
    import time

    print("🛡️  IoT Sentry - Packet Capture Test")
    print("=" * 50)
    print()

    def on_packet(src_ip, dst_ip, dst_port, protocol, size, timestamp):
        """Callback de ejemplo"""
        port_str = f":{dst_port}" if dst_port else ""
        print(f"📦 {src_ip} → {dst_ip}{port_str} ({protocol}) - {size} bytes")

    # Crear capturador
    capture = PacketCapture()
    capture.set_callback(on_packet)

    # Configurar dispositivos a monitorear (ejemplo)
    # En uso real, estas IPs vendrían del scanner
    capture.set_monitored_devices([
        "192.168.1.100",  # Ejemplo
        "192.168.1.50",
    ])

    # Iniciar captura
    print("⚠️  Iniciando captura (requiere permisos root/sudo)")
    print("   Presiona Ctrl+C para detener\n")

    try:
        capture.start()

        # Mantener vivo durante testing
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo...")
        capture.stop()

    print("✨ Test completado!")


if __name__ == "__main__":
    main()
