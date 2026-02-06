"""
IoT Sentry - Motor Principal

Coordina todos los componentes de la aplicación
"""

from datetime import datetime
from typing import List, Callable, Optional
import threading

from agent.scanner.device_identifier_comprehensive import ComprehensiveDeviceIdentifier
from agent.scanner import NetworkScanner
from agent.sniffer import PacketCapture, FlowTracker
from agent.analyzer import GeoLocator, BehaviorProfiler
from agent.database import get_db, Device, Flow, Alert


class IoTSentryEngine:
    """
    Motor principal que coordina todos los componentes
    """

    def __init__(self):
        """
        Inicializar motor
        """
        # Componentes
        self.scanner = NetworkScanner()
        self.identifier = ComprehensiveDeviceIdentifier()
        self.geo_locator = GeoLocator()
        self.packet_capture = None
        self.flow_tracker = None
        self.behavior_profiler = None

        # Base de datos
        self.db_context = None
        self.db_session = None

        # Estado
        self.running = False
        self.scan_interval = 300  # 5 minutos

        # Callbacks para GUI
        self.on_device_found_callback: Optional[Callable] = None
        self.on_alert_callback: Optional[Callable] = None
        self.on_stats_update_callback: Optional[Callable] = None

    def start(self):
        """
        Iniciar el motor
        """
        if self.running:
            print("⚠️  Motor ya está en ejecución")
            return

        print("🚀 Iniciando IoT Sentry Engine...")

        # Inicializar base de datos
        self.db_context = get_db()
        self.db_session = self.db_context.__enter__()

        # Inicializar componentes que requieren DB
        self.behavior_profiler = BehaviorProfiler(self.db_session)
        self.flow_tracker = FlowTracker(self.db_session)

        # Configurar packet capture
        self.packet_capture = PacketCapture()
        self.packet_capture.set_callback(self._on_packet_captured)

        # Hacer escaneo inicial
        self._scan_network()

        # Iniciar captura de paquetes
        self._start_capture()

        # Iniciar flow tracker
        self.flow_tracker.start()

        # Iniciar thread de escaneo periódico
        self.running = True
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()

        print("✅ IoT Sentry Engine iniciado")

    def stop(self):
        """
        Detener el motor
        """
        if not self.running:
            return

        print("🛑 Deteniendo IoT Sentry Engine...")

        self.running = False

        # Detener componentes
        if self.packet_capture:
            self.packet_capture.stop()

        if self.flow_tracker:
            self.flow_tracker.stop()

        # Cerrar base de datos
        if self.db_context:
            self.db_context.__exit__(None, None, None)

        # Cerrar geo locator
        self.geo_locator.close()

        print("✅ IoT Sentry Engine detenido")

    def _scan_network(self):
        """
        Escanear red y actualizar dispositivos
        """
        print("🔍 Escaneando red...")

        # Escanear
        devices_found = self.scanner.scan_network()

        # Procesar cada dispositivo encontrado
        for device_data in devices_found:
            # Identificar fabricante y tipo
            identification = self.identifier.identify_device(
                device_data['mac'],
                device_data['hostname']
            )

            # Buscar o crear dispositivo en DB
            device = self.db_session.query(Device).filter_by(
                mac_address=device_data['mac']
            ).first()

            if device:
                # Actualizar existente
                device.ip_address = device_data['ip']
                device.hostname = device_data['hostname']
                device.last_seen = device_data['timestamp']
            else:
                # Crear nuevo
                device = Device(
                    mac_address=device_data['mac'],
                    ip_address=device_data['ip'],
                    hostname=device_data['hostname'],
                    vendor=identification['vendor'],
                    device_type=identification['device_type'],
                    first_seen=device_data['timestamp'],
                    last_seen=device_data['timestamp']
                )
                self.db_session.add(device)

                # Notificar GUI si hay callback
                if self.on_device_found_callback:
                    self.on_device_found_callback(device)

        self.db_session.commit()
        print(f"✅ Escaneo completado: {len(devices_found)} dispositivos")

        # Actualizar IPs monitoreadas en packet capture
        self._update_monitored_devices()

    def _update_monitored_devices(self):
        """
        Actualizar lista de dispositivos a monitorear en packet capture
        """
        if not self.packet_capture:
            return

        # Obtener todas las IPs de dispositivos
        devices = self.db_session.query(Device).all()
        ip_addresses = [d.ip_address for d in devices if d.ip_address]

        self.packet_capture.set_monitored_devices(ip_addresses)

    def _start_capture(self):
        """
        Iniciar captura de paquetes
        """
        if not self.packet_capture:
            return

        try:
            self.packet_capture.start()
        except Exception as e:
            print(f"❌ Error iniciando captura: {e}")
            print("   ⚠️  Asegúrate de ejecutar con permisos de administrador")

    def _on_packet_captured(self, src_ip: str, dst_ip: str, dst_port: int,
                           protocol: str, size: int, timestamp: datetime):
        """
        Callback cuando se captura un paquete

        Args:
            src_ip: IP origen
            dst_ip: IP destino
            dst_port: Puerto destino
            protocol: Protocolo
            size: Tamaño
            timestamp: Timestamp
        """
        # Agregar a flow tracker
        if self.flow_tracker:
            self.flow_tracker.track_packet(
                src_ip, dst_ip, dst_port, protocol, size, timestamp
            )

        # Geolocalizar destino
        geo_info = self.geo_locator.geolocate(dst_ip)

        if geo_info:
            # Buscar device_id
            device = self.db_session.query(Device).filter_by(ip_address=src_ip).first()
            if not device:
                return

            # Analizar comportamiento
            alert_data = self.behavior_profiler.analyze_flow(
                device_id=device.id,
                dest_ip=dst_ip,
                dest_country=geo_info['country'],
                bytes_sent=size,
                timestamp=timestamp
            )

            # Crear alerta si se detectó anomalía
            if alert_data:
                alert = Alert(
                    device_id=device.id,
                    alert_type=alert_data['alert_type'],
                    severity=alert_data['severity'],
                    message=alert_data['message'],
                    metadata=alert_data['metadata'],
                    timestamp=timestamp
                )
                self.db_session.add(alert)
                self.db_session.commit()

                # Notificar GUI
                if self.on_alert_callback:
                    self.on_alert_callback(alert)

    def _scan_loop(self):
        """
        Loop de escaneo periódico
        """
        import time

        while self.running:
            time.sleep(self.scan_interval)
            if self.running:
                self._scan_network()

    def get_devices(self) -> List[Device]:
        """
        Obtener todos los dispositivos

        Returns:
            Lista de dispositivos
        """
        if not self.db_session:
            return []

        return self.db_session.query(Device).all()

    def get_device_flows(self, device_id: int, limit: int = 100) -> List[Flow]:
        """
        Obtener flujos de un dispositivo

        Args:
            device_id: ID del dispositivo
            limit: Límite de resultados

        Returns:
            Lista de flujos
        """
        if not self.db_session:
            return []

        return self.db_session.query(Flow).filter_by(
            device_id=device_id
        ).order_by(
            Flow.timestamp.desc()
        ).limit(limit).all()

    def get_alerts(self, limit: int = 50) -> List[Alert]:
        """
        Obtener alertas recientes

        Args:
            limit: Límite de resultados

        Returns:
            Lista de alertas
        """
        if not self.db_session:
            return []

        return self.db_session.query(Alert).order_by(
            Alert.timestamp.desc()
        ).limit(limit).all()

    def get_stats(self) -> dict:
        """
        Obtener estadísticas generales

        Returns:
            Dict con stats
        """
        if not self.db_session:
            return {}

        total_devices = self.db_session.query(Device).count()
        total_alerts = self.db_session.query(Alert).filter_by(acknowledged=False).count()
        total_flows = self.db_session.query(Flow).count()

        flow_stats = {}
        if self.flow_tracker:
            flow_stats = self.flow_tracker.get_stats()

        # Calcular latencia promedio (simple ping al gateway)
        avg_latency = self._calculate_average_latency()

        return {
            'total_devices': total_devices,
            'unread_alerts': total_alerts,
            'total_flows': total_flows,
            'capture_running': self.packet_capture.is_running() if self.packet_capture else False,
            'average_latency': avg_latency,
            **flow_stats
        }

    def _calculate_average_latency(self) -> Optional[float]:
        """
        Calcular latencia promedio usando ping al gateway

        Returns:
            Latencia promedio en ms o None si no se puede calcular
        """
        try:
            import subprocess
            import platform

            # Obtener gateway
            gateway = self.scanner.get_gateway()
            if not gateway:
                return None

            # Determinar comando ping según OS
            param = '-n' if platform.system().lower() == 'windows' else '-c'

            # Ejecutar ping (1 solo paquete para ser rápido)
            result = subprocess.run(
                ['ping', param, '1', gateway],
                capture_output=True,
                text=True,
                timeout=2
            )

            # Parsear resultado
            if result.returncode == 0:
                output = result.stdout
                # Buscar tiempo de respuesta
                if 'time=' in output:
                    time_str = output.split('time=')[1].split()[0]
                    return float(time_str.replace('ms', ''))
                elif 'tiempo=' in output:  # Spanish
                    time_str = output.split('tiempo=')[1].split()[0]
                    return float(time_str.replace('ms', ''))

            return None

        except Exception:
            return None

    # Métodos para configurar callbacks
    def set_device_found_callback(self, callback: Callable):
        """Configurar callback para nuevo dispositivo"""
        self.on_device_found_callback = callback

    def set_alert_callback(self, callback: Callable):
        """Configurar callback para nueva alerta"""
        self.on_alert_callback = callback

    def set_stats_update_callback(self, callback: Callable):
        """Configurar callback para actualización de stats"""
        self.on_stats_update_callback = callback
