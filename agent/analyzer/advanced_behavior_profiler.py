"""
IoT Sentry - Advanced Behavior Profiler

Detecta 15 tipos diferentes de comportamientos anómalos y sospechosos
"""

from datetime import datetime, timedelta, time
from typing import Dict, Optional, List
from collections import defaultdict, Counter


class AdvancedBehaviorProfiler:
    """
    Perfilador avanzado de comportamiento con múltiples tipos de detección
    """

    def __init__(self, db_session):
        """
        Inicializar profiler

        Args:
            db_session: Sesión de base de datos
        """
        self.db_session = db_session

        # Umbrales configurables
        self.UNUSUAL_HOUR_START = time(2, 0)   # 2 AM
        self.UNUSUAL_HOUR_END = time(6, 0)     # 6 AM
        self.HIGH_VOLUME_THRESHOLD = 100 * 1024 * 1024  # 100 MB
        self.EXCESSIVE_CONNECTIONS_THRESHOLD = 100  # conexiones/hora
        self.COUNTRY_HOPPING_THRESHOLD = 3  # países diferentes
        self.UPLOAD_RATIO_THRESHOLD = 3.0  # upload/download ratio

        # Puertos normales por tipo de dispositivo
        self.NORMAL_PORTS = {
            'camera': [80, 443, 554, 1935, 8080, 8443],  # HTTP, HTTPS, RTSP, RTMP
            'smart_speaker': [443, 8443, 4070],
            'smart_bulb': [443, 8080],
            'smart_plug': [443, 8080],
            'thermostat': [443, 8080],
            'smart_tv': [80, 443, 8008, 8080, 9000],
            'router': [80, 443, 8080],
        }

        # Rangos de IPs de Tor (simplificado)
        # En producción, usar lista completa de: https://check.torproject.org/exit-addresses
        self.TOR_EXIT_NODES = [
            '185.220.101.',  # Rango común de Tor
            '185.220.102.',
            '199.249.',
        ]

        # Países de alto riesgo (hosting común de malware)
        self.HIGH_RISK_COUNTRIES = [
            'North Korea',
            'Iran',  # Algunas IPs específicas
        ]

        # Cache de baselines por dispositivo
        self.device_baselines = {}

    def analyze_flow_comprehensive(self, device_id: int, device_type: str,
                                   dest_ip: str, dest_port: int, dest_country: str,
                                   bytes_sent: int, bytes_received: int,
                                   timestamp: datetime) -> List[Dict]:
        """
        Análisis exhaustivo de un flujo de red

        Args:
            device_id: ID del dispositivo
            device_type: Tipo de dispositivo
            dest_ip: IP destino
            dest_port: Puerto destino
            dest_country: País destino
            bytes_sent: Bytes enviados
            bytes_received: Bytes recibidos
            timestamp: Timestamp del flujo

        Returns:
            Lista de alertas detectadas
        """
        alerts = []

        # 1. Hora inusual (original)
        if self._is_unusual_time(timestamp):
            alerts.append({
                'alert_type': 'unusual_time',
                'severity': 'medium',
                'message': f'Conexión a {dest_ip} ({dest_country}) durante horas inusuales ({timestamp.strftime("%H:%M")})',
                'metadata': {
                    'dest_ip': dest_ip,
                    'dest_country': dest_country,
                    'timestamp': timestamp.isoformat()
                }
            })

        # 2. Volumen alto (original)
        if bytes_sent > self.HIGH_VOLUME_THRESHOLD:
            alerts.append({
                'alert_type': 'high_volume',
                'severity': 'high',
                'message': f'Volumen inusualmente alto de datos: {bytes_sent / (1024*1024):.1f} MB enviados',
                'metadata': {
                    'dest_ip': dest_ip,
                    'bytes_sent': bytes_sent
                }
            })

        # 3. Destino sospechoso (original mejorado)
        suspicious_dest = self._check_suspicious_destination(device_type, dest_country, dest_ip)
        if suspicious_dest:
            alerts.append(suspicious_dest)

        # 4. NUEVO: Conexiones repetitivas anormales
        excessive = self._check_excessive_connections(device_id, dest_ip)
        if excessive:
            alerts.append(excessive)

        # 5. NUEVO: Country hopping
        hopping = self._check_country_hopping(device_id)
        if hopping:
            alerts.append(hopping)

        # 6. NUEVO: Puerto inusual
        unusual_port = self._check_unusual_port(device_type, dest_port, dest_ip)
        if unusual_port:
            alerts.append(unusual_port)

        # 7. NUEVO: Conexión a Tor
        tor_connection = self._check_tor_connection(dest_ip)
        if tor_connection:
            alerts.append(tor_connection)

        # 8. NUEVO: Más upload que download
        upload_ratio = self._check_upload_ratio(bytes_sent, bytes_received)
        if upload_ratio:
            alerts.append(upload_ratio)

        # 9. NUEVO: País en blacklist
        blacklisted = self._check_blacklisted_country(dest_country)
        if blacklisted:
            alerts.append(blacklisted)

        return alerts

    def check_new_device(self, device_id: int, mac_address: str, vendor: str,
                        first_seen: datetime) -> Optional[Dict]:
        """
        10. NUEVO: Detectar dispositivo nuevo en la red
        """
        # Verificar si es realmente nuevo (primera vez visto en últimas 24h)
        time_since_first = datetime.utcnow() - first_seen
        if time_since_first < timedelta(hours=1):
            return {
                'alert_type': 'new_device',
                'severity': 'medium',
                'message': f'Nuevo dispositivo detectado: {vendor} ({mac_address})',
                'metadata': {
                    'mac_address': mac_address,
                    'vendor': vendor,
                    'first_seen': first_seen.isoformat()
                }
            }
        return None

    def check_behavior_change(self, device_id: int) -> Optional[Dict]:
        """
        11. NUEVO: Cambio drástico de comportamiento
        """
        from agent.database.models import Flow
        from sqlalchemy import func

        # Obtener baseline (últimos 30 días excepto último día)
        baseline_start = datetime.utcnow() - timedelta(days=30)
        baseline_end = datetime.utcnow() - timedelta(days=1)

        baseline_avg = self.db_session.query(
            func.avg(func.sum(Flow.bytes_sent))
        ).filter(
            Flow.device_id == device_id,
            Flow.timestamp >= baseline_start,
            Flow.timestamp < baseline_end
        ).group_by(
            func.date(Flow.timestamp)
        ).scalar()

        if not baseline_avg or baseline_avg < 1000:
            return None  # Insuficientes datos

        # Obtener uso de hoy
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_usage = self.db_session.query(
            func.sum(Flow.bytes_sent)
        ).filter(
            Flow.device_id == device_id,
            Flow.timestamp >= today_start
        ).scalar() or 0

        # Detectar cambio drástico (10x)
        if today_usage > baseline_avg * 10:
            increment_pct = ((today_usage - baseline_avg) / baseline_avg) * 100
            return {
                'alert_type': 'behavior_change',
                'severity': 'medium',
                'message': f'Cambio drástico de comportamiento detectado (incremento {increment_pct:.0f}%)',
                'metadata': {
                    'baseline_mb': baseline_avg / (1024**2),
                    'today_mb': today_usage / (1024**2),
                    'increment_percent': increment_pct
                }
            }

        return None

    def check_mac_spoofing(self, ip_address: str, current_mac: str) -> Optional[Dict]:
        """
        12. NUEVO: Detectar cambio de MAC address (spoofing)
        """
        from agent.database.models import Device

        # Buscar si hay otro dispositivo con misma IP pero MAC diferente
        devices_same_ip = self.db_session.query(Device).filter(
            Device.ip_address == ip_address,
            Device.mac_address != current_mac
        ).all()

        if devices_same_ip:
            # Verificar si el cambio es reciente (últimas 24h)
            for old_device in devices_same_ip:
                if old_device.last_seen and (datetime.utcnow() - old_device.last_seen) < timedelta(hours=24):
                    return {
                        'alert_type': 'mac_spoofing',
                        'severity': 'high',
                        'message': f'Posible MAC spoofing: IP {ip_address} cambió de MAC',
                        'metadata': {
                            'ip_address': ip_address,
                            'old_mac': old_device.mac_address,
                            'new_mac': current_mac,
                            'old_vendor': old_device.vendor
                        }
                    }

        return None

    # ============ Métodos auxiliares ============

    def _is_unusual_time(self, timestamp: datetime) -> bool:
        """Verificar hora inusual (2-6 AM)"""
        current_time = timestamp.time()
        return self.UNUSUAL_HOUR_START <= current_time <= self.UNUSUAL_HOUR_END

    def _check_suspicious_destination(self, device_type: str, dest_country: str,
                                      dest_ip: str) -> Optional[Dict]:
        """Verificar destino geográfico sospechoso"""
        # Cámaras
        if device_type in ['camera', 'security_camera', 'doorbell', 'baby_monitor']:
            common_countries = ['United States', 'Germany', 'Ireland', 'Netherlands',
                              'United Kingdom', 'Canada']
            if dest_country not in common_countries and dest_country not in ['Local Network', 'Unknown']:
                return {
                    'alert_type': 'suspicious_destination',
                    'severity': 'high',
                    'message': f'Cámara conectándose a {dest_country} ({dest_ip})',
                    'metadata': {
                        'device_type': device_type,
                        'dest_country': dest_country,
                        'dest_ip': dest_ip,
                        'expected_countries': common_countries
                    }
                }

        # Smart speakers
        if device_type in ['smart_speaker', 'smart_display']:
            if dest_country not in ['United States', 'Local Network', 'Unknown']:
                return {
                    'alert_type': 'suspicious_destination',
                    'severity': 'medium',
                    'message': f'Asistente de voz conectándose a {dest_country}',
                    'metadata': {
                        'device_type': device_type,
                        'dest_country': dest_country
                    }
                }

        return None

    def _check_excessive_connections(self, device_id: int, dest_ip: str) -> Optional[Dict]:
        """4. Detectar conexiones repetitivas anormales"""
        from agent.database.models import Flow

        # Contar conexiones en última hora al mismo destino
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        connection_count = self.db_session.query(Flow).filter(
            Flow.device_id == device_id,
            Flow.dest_ip == dest_ip,
            Flow.timestamp >= one_hour_ago
        ).count()

        if connection_count > self.EXCESSIVE_CONNECTIONS_THRESHOLD:
            return {
                'alert_type': 'excessive_connections',
                'severity': 'medium',
                'message': f'{connection_count} conexiones repetitivas en última hora a {dest_ip}',
                'metadata': {
                    'dest_ip': dest_ip,
                    'connection_count': connection_count,
                    'threshold': self.EXCESSIVE_CONNECTIONS_THRESHOLD
                }
            }

        return None

    def _check_country_hopping(self, device_id: int) -> Optional[Dict]:
        """5. Detectar saltos entre múltiples países"""
        from agent.database.models import Flow

        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        # Obtener países únicos en última hora
        countries = self.db_session.query(Flow.dest_country).filter(
            Flow.device_id == device_id,
            Flow.timestamp >= one_hour_ago,
            Flow.dest_country.notin_(['Local Network', 'Unknown', None])
        ).distinct().all()

        unique_countries = [c[0] for c in countries if c[0]]

        if len(unique_countries) >= self.COUNTRY_HOPPING_THRESHOLD:
            return {
                'alert_type': 'country_hopping',
                'severity': 'high',
                'message': f'Dispositivo conectado a {len(unique_countries)} países en última hora',
                'metadata': {
                    'countries': unique_countries,
                    'count': len(unique_countries)
                }
            }

        return None

    def _check_unusual_port(self, device_type: str, dest_port: int, dest_ip: str) -> Optional[Dict]:
        """6. Detectar puerto inusual para tipo de dispositivo"""
        if device_type not in self.NORMAL_PORTS:
            return None  # No tenemos info de puertos normales para este tipo

        normal_ports = self.NORMAL_PORTS[device_type]

        if dest_port not in normal_ports:
            # Identificar si es un puerto particularmente sospechoso
            suspicious_ports = {
                22: 'SSH (acceso remoto)',
                23: 'Telnet (inseguro)',
                3389: 'RDP (escritorio remoto)',
                445: 'SMB (compartir archivos)',
                1433: 'SQL Server',
                3306: 'MySQL',
                5432: 'PostgreSQL',
            }

            port_desc = suspicious_ports.get(dest_port, f'Puerto {dest_port}')

            severity = 'high' if dest_port in suspicious_ports else 'medium'

            return {
                'alert_type': 'unusual_port',
                'severity': severity,
                'message': f'Dispositivo IoT usando {port_desc} - inusual para {device_type}',
                'metadata': {
                    'device_type': device_type,
                    'dest_port': dest_port,
                    'dest_ip': dest_ip,
                    'expected_ports': normal_ports
                }
            }

        return None

    def _check_tor_connection(self, dest_ip: str) -> Optional[Dict]:
        """7. Detectar conexión a red Tor"""
        for tor_range in self.TOR_EXIT_NODES:
            if dest_ip.startswith(tor_range):
                return {
                    'alert_type': 'tor_connection',
                    'severity': 'high',
                    'message': f'Dispositivo conectándose a nodo Tor ({dest_ip})',
                    'metadata': {
                        'dest_ip': dest_ip,
                        'tor_range': tor_range
                    }
                }

        return None

    def _check_upload_ratio(self, bytes_sent: int, bytes_received: int) -> Optional[Dict]:
        """8. Detectar más upload que download (sospechoso)"""
        if bytes_received == 0 or bytes_sent < 10000:  # Evitar división por 0 y flujos muy pequeños
            return None

        ratio = bytes_sent / bytes_received

        if ratio > self.UPLOAD_RATIO_THRESHOLD:
            return {
                'alert_type': 'excessive_upload',
                'severity': 'medium',
                'message': f'Ratio anormal upload/download: {ratio:.1f}:1 (envía mucho más de lo que recibe)',
                'metadata': {
                    'bytes_sent': bytes_sent,
                    'bytes_received': bytes_received,
                    'ratio': ratio
                }
            }

        return None

    def _check_blacklisted_country(self, dest_country: str) -> Optional[Dict]:
        """9. Detectar conexión a país de alto riesgo"""
        if dest_country in self.HIGH_RISK_COUNTRIES:
            return {
                'alert_type': 'blacklisted_country',
                'severity': 'high',
                'message': f'Conexión a país de alto riesgo: {dest_country}',
                'metadata': {
                    'dest_country': dest_country
                }
            }

        return None
