"""
IoT Sentry - Flow Tracker

Agrega paquetes en flujos de red y los persiste en base de datos
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple
import threading


class FlowTracker:
    """
    Rastreador de flujos de red

    Un "flujo" es una conexión única definida por:
    (src_ip, dst_ip, dst_port, protocol)
    """

    def __init__(self, db_session, flush_interval: int = 30):
        """
        Inicializar tracker

        Args:
            db_session: Sesión de base de datos SQLAlchemy
            flush_interval: Intervalo en segundos para guardar flujos en DB
        """
        self.db_session = db_session
        self.flush_interval = flush_interval

        # Diccionario de flujos activos
        # Key: (src_ip, dst_ip, dst_port, protocol)
        # Value: {'bytes': int, 'packets': int, 'last_seen': datetime}
        self.active_flows: Dict[Tuple, dict] = {}

        # Lock para thread-safety
        self.lock = threading.Lock()

        # Thread de flush periódico
        self.flush_thread = None
        self.running = False

    def track_packet(self, src_ip: str, dst_ip: str, dst_port: int,
                     protocol: str, size: int, timestamp: datetime):
        """
        Agregar paquete a flujo existente o crear nuevo flujo

        Args:
            src_ip: IP origen
            dst_ip: IP destino
            dst_port: Puerto destino
            protocol: Protocolo (TCP, UDP, etc.)
            size: Tamaño del paquete en bytes
            timestamp: Timestamp de captura
        """
        # Crear key del flujo
        flow_key = (src_ip, dst_ip, dst_port, protocol)

        with self.lock:
            if flow_key in self.active_flows:
                # Actualizar flujo existente
                self.active_flows[flow_key]['bytes'] += size
                self.active_flows[flow_key]['packets'] += 1
                self.active_flows[flow_key]['last_seen'] = timestamp
            else:
                # Crear nuevo flujo
                self.active_flows[flow_key] = {
                    'bytes': size,
                    'packets': 1,
                    'first_seen': timestamp,
                    'last_seen': timestamp
                }

    def _flush_flows(self):
        """
        Guardar flujos activos en base de datos y limpiar antiguos
        """
        from agent.database.models import Flow, Device

        with self.lock:
            if not self.active_flows:
                return

            flows_to_save = []
            now = datetime.utcnow()

            # Procesar cada flujo
            for (src_ip, dst_ip, dst_port, protocol), data in list(self.active_flows.items()):
                # Buscar device_id
                device = self.db_session.query(Device).filter_by(ip_address=src_ip).first()
                if not device:
                    # Si el dispositivo no existe, skip
                    continue

                # Crear registro de flujo
                flow = Flow(
                    device_id=device.id,
                    dest_ip=dst_ip,
                    dest_port=dst_port,
                    protocol=protocol,
                    bytes_sent=data['bytes'],
                    packets_sent=data['packets'],
                    timestamp=data['first_seen']
                )

                flows_to_save.append(flow)

                # Limpiar flujos antiguos (> 5 minutos de inactividad)
                if now - data['last_seen'] > timedelta(minutes=5):
                    del self.active_flows[(src_ip, dst_ip, dst_port, protocol)]

            # Guardar en DB
            if flows_to_save:
                try:
                    self.db_session.bulk_save_objects(flows_to_save)
                    self.db_session.commit()
                    print(f"💾 Guardados {len(flows_to_save)} flujos en DB")
                except Exception as e:
                    print(f"❌ Error guardando flujos: {e}")
                    self.db_session.rollback()

    def _flush_loop(self):
        """
        Loop de flush periódico (ejecutado en thread)
        """
        import time

        while self.running:
            time.sleep(self.flush_interval)
            self._flush_flows()

    def start(self):
        """
        Iniciar flush periódico de flujos
        """
        if self.running:
            return

        self.running = True
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()
        print(f"✅ Flow tracker iniciado (flush cada {self.flush_interval}s)")

    def stop(self):
        """
        Detener tracker y hacer flush final
        """
        if not self.running:
            return

        self.running = False

        # Flush final
        self._flush_flows()

        if self.flush_thread:
            self.flush_thread.join(timeout=2)

        print("✅ Flow tracker detenido")

    def get_stats(self) -> dict:
        """
        Obtener estadísticas de flujos activos

        Returns:
            Dict con stats
        """
        with self.lock:
            total_flows = len(self.active_flows)
            total_bytes = sum(f['bytes'] for f in self.active_flows.values())
            total_packets = sum(f['packets'] for f in self.active_flows.values())

            return {
                'active_flows': total_flows,
                'total_bytes': total_bytes,
                'total_packets': total_packets
            }
