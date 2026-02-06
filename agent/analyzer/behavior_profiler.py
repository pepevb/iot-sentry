"""
IoT Sentry - Behavior Profiler

Detecta comportamientos anómalos en dispositivos IoT
"""

from datetime import datetime, time
from typing import Dict, Optional
from collections import defaultdict


class BehaviorProfiler:
    """
    Perfilador de comportamiento de dispositivos

    Detecta:
    - Conexiones a horas inusuales
    - Volúmenes anormales de datos
    - Destinos inesperados geográficamente
    """

    def __init__(self, db_session):
        """
        Inicializar profiler

        Args:
            db_session: Sesión de base de datos
        """
        self.db_session = db_session

        # Perfiles de dispositivos (calculados dinámicamente)
        self.device_profiles: Dict[int, dict] = defaultdict(dict)

        # Umbrales
        self.UNUSUAL_HOUR_START = time(2, 0)   # 2 AM
        self.UNUSUAL_HOUR_END = time(6, 0)     # 6 AM
        self.HIGH_VOLUME_THRESHOLD = 100 * 1024 * 1024  # 100 MB

    def analyze_flow(self, device_id: int, dest_ip: str, dest_country: str,
                     bytes_sent: int, timestamp: datetime) -> Optional[Dict]:
        """
        Analizar flujo y detectar anomalías

        Args:
            device_id: ID del dispositivo
            dest_ip: IP destino
            dest_country: País destino
            bytes_sent: Bytes enviados
            timestamp: Timestamp del flujo

        Returns:
            Dict con alerta si se detecta anomalía, None si todo normal:
            {
                'alert_type': 'unusual_time' | 'high_volume' | 'suspicious_destination',
                'severity': 'low' | 'medium' | 'high',
                'message': str,
                'metadata': dict
            }
        """
        alerts = []

        # 1. Verificar hora inusual
        if self._is_unusual_time(timestamp):
            alerts.append({
                'alert_type': 'unusual_time',
                'severity': 'medium',
                'message': f'Conexión a {dest_ip} durante horas inusuales ({timestamp.strftime("%H:%M")})',
                'metadata': {
                    'dest_ip': dest_ip,
                    'dest_country': dest_country,
                    'timestamp': timestamp.isoformat()
                }
            })

        # 2. Verificar volumen alto
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

        # 3. Verificar destino sospechoso
        suspicious_alert = self._check_suspicious_destination(
            device_id, dest_country, dest_ip
        )
        if suspicious_alert:
            alerts.append(suspicious_alert)

        # Retornar la alerta más severa
        if alerts:
            # Ordenar por severidad
            severity_order = {'high': 3, 'medium': 2, 'low': 1}
            alerts.sort(key=lambda x: severity_order[x['severity']], reverse=True)
            return alerts[0]

        return None

    def _is_unusual_time(self, timestamp: datetime) -> bool:
        """
        Verificar si el timestamp está en horas inusuales

        Args:
            timestamp: Timestamp a verificar

        Returns:
            True si es hora inusual (2 AM - 6 AM)
        """
        current_time = timestamp.time()
        return self.UNUSUAL_HOUR_START <= current_time <= self.UNUSUAL_HOUR_END

    def _check_suspicious_destination(self, device_id: int, dest_country: str,
                                      dest_ip: str) -> Optional[Dict]:
        """
        Verificar si el destino es sospechoso para este dispositivo

        Args:
            device_id: ID del dispositivo
            dest_country: País destino
            dest_ip: IP destino

        Returns:
            Alerta si es sospechoso
        """
        from agent.database.models import Device

        # Obtener tipo de dispositivo
        device = self.db_session.query(Device).filter_by(id=device_id).first()
        if not device:
            return None

        # Heurísticas específicas por tipo de dispositivo
        device_type = device.device_type

        # Cámaras conectándose a países lejanos
        if device_type == 'camera':
            # Lista de países comunes para servicios cloud de cámaras (US, EU)
            common_countries = ['United States', 'Germany', 'Ireland', 'Netherlands', 'United Kingdom']

            if dest_country not in common_countries and dest_country not in ['Local Network', 'Unknown']:
                return {
                    'alert_type': 'suspicious_destination',
                    'severity': 'high',
                    'message': f'Cámara conectándose a {dest_country} ({dest_ip})',
                    'metadata': {
                        'device_type': device_type,
                        'dest_country': dest_country,
                        'dest_ip': dest_ip
                    }
                }

        # Smart speakers conectándose a países inusuales
        if device_type == 'smart_speaker':
            # Alexa/Google normalmente usan US servers
            if dest_country not in ['United States', 'Local Network', 'Unknown']:
                return {
                    'alert_type': 'suspicious_destination',
                    'severity': 'medium',
                    'message': f'Smart speaker conectándose a {dest_country}',
                    'metadata': {
                        'device_type': device_type,
                        'dest_country': dest_country
                    }
                }

        return None

    def calculate_device_baseline(self, device_id: int):
        """
        Calcular comportamiento baseline de un dispositivo

        Args:
            device_id: ID del dispositivo

        Returns:
            Dict con estadísticas baseline
        """
        from agent.database.models import Flow
        from sqlalchemy import func

        # Calcular estadísticas de los últimos 7 días
        stats = self.db_session.query(
            func.avg(Flow.bytes_sent).label('avg_bytes'),
            func.max(Flow.bytes_sent).label('max_bytes'),
            func.count(Flow.id).label('total_flows')
        ).filter(
            Flow.device_id == device_id
        ).first()

        if stats and stats.total_flows > 0:
            baseline = {
                'avg_bytes': stats.avg_bytes or 0,
                'max_bytes': stats.max_bytes or 0,
                'total_flows': stats.total_flows
            }
            self.device_profiles[device_id] = baseline
            return baseline

        return None
