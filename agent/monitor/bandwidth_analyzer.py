"""
IoT Sentry - Analizador de Ancho de Banda

Detecta "vampiros de ancho de banda" y analiza consumo por dispositivo
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class BandwidthAnalyzer:
    """Analizador de consumo de ancho de banda"""

    def __init__(self, db_session):
        """
        Inicializar analizador

        Args:
            db_session: Sesión de base de datos
        """
        self.db_session = db_session

    def get_bandwidth_by_device(self, hours: int = 1) -> List[Dict]:
        """
        Obtener consumo de ancho de banda por dispositivo

        Args:
            hours: Horas a analizar (hacia atrás desde ahora)

        Returns:
            Lista de dispositivos con su consumo [{device_id, bytes, mbps}, ...]
        """
        from agent.database.models import Device, Flow

        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Query: Sumar bytes por dispositivo
        from sqlalchemy import func

        results = self.db_session.query(
            Device.id,
            Device.hostname,
            Device.vendor,
            Device.device_type,
            Device.ip_address,
            func.sum(Flow.bytes_sent).label('total_bytes'),
            func.count(Flow.id).label('total_flows')
        ).join(
            Flow, Device.id == Flow.device_id
        ).filter(
            Flow.timestamp >= cutoff
        ).group_by(
            Device.id
        ).order_by(
            func.sum(Flow.bytes_sent).desc()
        ).all()

        # Convertir a lista de dicts
        devices = []
        total_bytes = sum(r.total_bytes or 0 for r in results)

        for r in results:
            bytes_sent = r.total_bytes or 0
            mbps = (bytes_sent * 8) / (hours * 3600 * 1_000_000)  # Convertir a Mbps promedio
            percentage = (bytes_sent / total_bytes * 100) if total_bytes > 0 else 0

            devices.append({
                'device_id': r.id,
                'hostname': r.hostname or 'Unknown',
                'vendor': r.vendor or 'Unknown',
                'device_type': r.device_type or 'unknown',
                'ip_address': r.ip_address,
                'bytes_sent': bytes_sent,
                'mbps_avg': round(mbps, 2),
                'percentage': round(percentage, 1),
                'total_flows': r.total_flows
            })

        return devices

    def detect_bandwidth_hogs(self, hours: int = 1, threshold_percentage: float = 20.0) -> List[Dict]:
        """
        Detectar "vampiros de ancho de banda"

        Args:
            hours: Horas a analizar
            threshold_percentage: Porcentaje mínimo para considerar vampiro (default 20%)

        Returns:
            Lista de vampiros con análisis
        """
        devices = self.get_bandwidth_by_device(hours)

        # Si no hay datos reales, no reportar vampiros
        total_bytes = sum(d['bytes_sent'] for d in devices)
        if total_bytes < 1000:  # Menos de 1KB = no hay datos reales
            return []

        vampires = []

        for device in devices:
            # Solo considerar vampiro si tiene consumo real (> 10KB)
            if device['bytes_sent'] < 10000:
                continue

            if device['percentage'] >= threshold_percentage:
                # Determinar severidad
                if device['percentage'] >= 50:
                    severity = 'critical'
                    emoji = '🔴'
                elif device['percentage'] >= 30:
                    severity = 'high'
                    emoji = '🟠'
                else:
                    severity = 'medium'
                    emoji = '🟡'

                vampires.append({
                    **device,
                    'severity': severity,
                    'emoji': emoji,
                    'message': f"{device['hostname']} está consumiendo {device['percentage']:.0f}% del ancho de banda"
                })

        return vampires

    def get_traffic_timeline(self, device_id: Optional[int] = None, hours: int = 24) -> List[Dict]:
        """
        Obtener timeline de tráfico (para gráficos)

        Args:
            device_id: ID del dispositivo (None = todos)
            hours: Horas de historial

        Returns:
            Lista de puntos temporales [{timestamp, bytes}, ...]
        """
        from agent.database.models import Flow
        from sqlalchemy import func

        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Agrupar por hora
        query = self.db_session.query(
            func.strftime('%Y-%m-%d %H:00:00', Flow.timestamp).label('hour'),
            func.sum(Flow.bytes_sent).label('total_bytes'),
            func.count(Flow.id).label('flow_count')
        ).filter(
            Flow.timestamp >= cutoff
        )

        if device_id:
            query = query.filter(Flow.device_id == device_id)

        query = query.group_by('hour').order_by('hour')

        results = query.all()

        timeline = []
        for r in results:
            timeline.append({
                'timestamp': datetime.strptime(r.hour, '%Y-%m-%d %H:%M:%S'),
                'bytes': r.total_bytes or 0,
                'mbps': ((r.total_bytes or 0) * 8) / (3600 * 1_000_000),  # Mbps promedio en esa hora
                'flows': r.flow_count
            })

        return timeline

    def get_top_destinations(self, device_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """
        Obtener destinos más frecuentes

        Args:
            device_id: ID del dispositivo (None = todos)
            limit: Número de resultados

        Returns:
            Lista de destinos [{dest_ip, dest_country, bytes, flows}, ...]
        """
        from agent.database.models import Flow
        from sqlalchemy import func

        query = self.db_session.query(
            Flow.dest_ip,
            Flow.dest_country,
            Flow.dest_city,
            func.sum(Flow.bytes_sent).label('total_bytes'),
            func.count(Flow.id).label('flow_count')
        )

        if device_id:
            query = query.filter(Flow.device_id == device_id)

        query = query.group_by(
            Flow.dest_ip, Flow.dest_country, Flow.dest_city
        ).order_by(
            func.sum(Flow.bytes_sent).desc()
        ).limit(limit)

        results = query.all()

        destinations = []
        for r in results:
            destinations.append({
                'dest_ip': r.dest_ip,
                'dest_country': r.dest_country or 'Unknown',
                'dest_city': r.dest_city or 'Unknown',
                'bytes_sent': r.total_bytes or 0,
                'mb_sent': round((r.total_bytes or 0) / (1024 * 1024), 2),
                'flow_count': r.flow_count
            })

        return destinations

    def generate_bandwidth_report(self, hours: int = 24) -> str:
        """
        Generar reporte de ancho de banda en texto

        Args:
            hours: Horas a analizar

        Returns:
            Reporte en texto
        """
        report = f"📊 REPORTE DE ANCHO DE BANDA (últimas {hours}h)\n"
        report += "=" * 60 + "\n\n"

        # Top consumidores
        devices = self.get_bandwidth_by_device(hours)

        if not devices:
            report += "ℹ️  No hay datos de tráfico disponibles\n"
            return report

        report += f"🌐 Consumo Total: {sum(d['bytes_sent'] for d in devices) / (1024**3):.2f} GB\n\n"

        report += "📱 Top Dispositivos:\n"
        for i, device in enumerate(devices[:5], 1):
            bar = '█' * int(device['percentage'] / 5) + '░' * (20 - int(device['percentage'] / 5))
            report += f"{i}. {device['hostname'][:25]:<25} {bar} {device['percentage']:5.1f}% ({device['mbps_avg']:.1f} Mbps)\n"

        report += "\n"

        # Vampiros
        vampires = self.detect_bandwidth_hogs(hours, threshold_percentage=15.0)

        if vampires:
            report += "⚠️  VAMPIROS DE ANCHO DE BANDA DETECTADOS:\n\n"
            for vamp in vampires:
                report += f"{vamp['emoji']} {vamp['message']}\n"
                report += f"   {vamp['bytes_sent'] / (1024**2):.1f} MB enviados en {hours}h\n"
                report += f"   Promedio: {vamp['mbps_avg']:.1f} Mbps\n\n"

            report += "💡 Recomendaciones:\n"
            report += "   → Pausar streaming de video/gaming durante videollamadas\n"
            report += "   → Configurar backups automáticos para horarios nocturnos\n"
            report += "   → Considerar upgrade de plan de internet\n\n"
        else:
            report += "✅ No se detectaron vampiros de ancho de banda\n\n"

        return report


from typing import Optional


def main():
    """Testing (requiere DB con datos)"""
    print("🛡️  IoT Sentry - Bandwidth Analyzer Test")
    print("=" * 50)
    print()

    # Este test requiere una DB poblada
    print("ℹ️  Este módulo requiere una base de datos con datos de flujos")
    print("   Ejecuta la aplicación completa para generar datos primero")


if __name__ == "__main__":
    main()
