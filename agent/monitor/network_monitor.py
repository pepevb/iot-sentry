"""
IoT Sentry - Monitor de Red

Mide latencia, detecta problemas de red y analiza rendimiento
"""

import time
import subprocess
import platform
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque


class NetworkMonitor:
    """Monitor de rendimiento de red y detector de LAG"""

    def __init__(self):
        """Inicializar monitor"""
        self.running = False
        self.monitor_thread = None

        # Hosts a monitorear
        self.test_hosts = {
            'router': '192.168.1.1',  # Se actualizará con gateway real
            'google_dns': '8.8.8.8',
            'cloudflare_dns': '1.1.1.1',
            'opendns': '208.67.222.222'
        }

        # Historial de latencia (últimas 100 mediciones por host)
        self.latency_history: Dict[str, deque] = {
            host: deque(maxlen=100) for host in self.test_hosts.keys()
        }

        # Estadísticas actuales
        self.current_stats = {
            'router_latency': None,
            'internet_latency': None,
            'packet_loss': 0.0,
            'jitter': 0.0,
            'status': 'unknown'
        }

        # Intervalo de medición (segundos)
        self.measure_interval = 10

    def set_router_ip(self, router_ip: str):
        """
        Configurar IP del router

        Args:
            router_ip: IP del gateway/router
        """
        self.test_hosts['router'] = router_ip
        self.latency_history['router'] = deque(maxlen=100)

    def ping_host(self, host: str, count: int = 1, timeout: int = 2) -> Optional[float]:
        """
        Hacer ping a un host y medir latencia

        Args:
            host: IP o hostname
            count: Número de pings
            timeout: Timeout en segundos

        Returns:
            Latencia promedio en ms o None si falla
        """
        try:
            # Comando ping según plataforma
            system = platform.system().lower()

            if system == 'windows':
                cmd = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
            else:  # Linux, macOS
                cmd = ['ping', '-c', str(count), '-W', str(timeout), host]

            # Ejecutar ping
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 1
            )

            # Parsear resultado
            output = result.stdout

            if system == 'windows':
                # Windows: "Average = XXms"
                if 'Average' in output:
                    latency = float(output.split('Average = ')[1].split('ms')[0])
                    return latency
            else:
                # Linux/macOS: "round-trip min/avg/max/stddev = X/Y/Z/W ms"
                if 'avg' in output or 'rtt' in output:
                    # Buscar patrón: min/avg/max
                    parts = output.split('=')[-1].split('/')
                    if len(parts) >= 2:
                        avg_latency = float(parts[1].strip())
                        return avg_latency

            return None

        except Exception as e:
            return None

    def measure_all_latencies(self) -> Dict[str, Optional[float]]:
        """
        Medir latencia a todos los hosts

        Returns:
            Dict con latencias {host: latency_ms}
        """
        results = {}

        for name, host in self.test_hosts.items():
            latency = self.ping_host(host, count=3)
            results[name] = latency

            # Guardar en historial
            if latency is not None:
                self.latency_history[name].append({
                    'timestamp': datetime.utcnow(),
                    'latency': latency
                })

        return results

    def calculate_jitter(self, host: str = 'google_dns') -> float:
        """
        Calcular jitter (variación de latencia)

        Args:
            host: Host a analizar

        Returns:
            Jitter en ms
        """
        if host not in self.latency_history:
            return 0.0

        history = self.latency_history[host]
        if len(history) < 2:
            return 0.0

        # Calcular diferencias entre mediciones consecutivas
        latencies = [entry['latency'] for entry in history]
        differences = [abs(latencies[i] - latencies[i-1]) for i in range(1, len(latencies))]

        # Jitter = promedio de las diferencias
        jitter = sum(differences) / len(differences) if differences else 0.0

        return round(jitter, 2)

    def calculate_packet_loss(self, host: str = 'google_dns') -> float:
        """
        Estimar pérdida de paquetes

        Args:
            host: Host a analizar

        Returns:
            Porcentaje de pérdida (0-100)
        """
        if host not in self.latency_history:
            return 0.0

        history = self.latency_history[host]
        if len(history) < 10:
            return 0.0

        # Contar cuántos pings exitosos vs fallidos
        # (Nota: en este diseño, solo guardamos exitosos)
        # Para mejorar, deberíamos registrar intentos fallidos también

        return 0.0  # Por ahora

    def analyze_network_health(self) -> Dict:
        """
        Analizar salud general de la red

        Returns:
            Dict con análisis completo
        """
        # Medir latencias actuales
        latencies = self.measure_all_latencies()

        router_latency = latencies.get('router')
        internet_latency = latencies.get('google_dns') or latencies.get('cloudflare_dns')

        # Calcular jitter
        jitter = self.calculate_jitter()

        # Determinar estado
        status = 'excellent'
        issues = []
        recommendations = []

        # Analizar latencia al router
        if router_latency is None:
            status = 'critical'
            issues.append('❌ No se puede alcanzar el router')
            recommendations.append('→ Verificar conexión física al router')
        elif router_latency > 100:
            status = 'poor'
            issues.append(f'⚠️ Latencia alta al router: {router_latency:.0f}ms')
            recommendations.append('→ Posible congestión en red local')
            recommendations.append('→ Verificar dispositivos consumiendo mucho ancho de banda')
        elif router_latency > 50:
            status = 'fair'
            issues.append(f'⚠️ Latencia moderada al router: {router_latency:.0f}ms')

        # Analizar latencia a internet
        if internet_latency is None:
            status = 'critical'
            issues.append('❌ Sin conexión a internet')
            recommendations.append('→ Verificar estado del ISP')
        elif internet_latency > 150:
            if status == 'excellent':
                status = 'fair'
            issues.append(f'⚠️ Latencia alta a internet: {internet_latency:.0f}ms')
            recommendations.append('→ Problema puede estar en el ISP')
            recommendations.append('→ Contactar proveedor de internet')

        # Analizar jitter
        if jitter > 30:
            if status in ['excellent', 'good']:
                status = 'fair'
            issues.append(f'⚠️ Jitter alto: {jitter:.0f}ms')
            recommendations.append('→ Red inestable - malo para videollamadas y gaming')
            recommendations.append('→ Reducir número de dispositivos activos')

        if not issues:
            issues.append('✅ Red funcionando óptimamente')

        # Actualizar stats actuales
        self.current_stats = {
            'router_latency': router_latency,
            'internet_latency': internet_latency,
            'packet_loss': 0.0,
            'jitter': jitter,
            'status': status,
            'issues': issues,
            'recommendations': recommendations,
            'all_latencies': latencies,
            'timestamp': datetime.utcnow()
        }

        return self.current_stats

    def get_diagnosis(self) -> str:
        """
        Obtener diagnóstico en texto legible

        Returns:
            String con diagnóstico completo
        """
        stats = self.current_stats

        status_emoji = {
            'excellent': '🟢',
            'good': '🟢',
            'fair': '🟡',
            'poor': '🟠',
            'critical': '🔴',
            'unknown': '⚪'
        }

        diagnosis = f"{status_emoji[stats['status']]} Estado de Red: {stats['status'].upper()}\n\n"

        # Latencias
        diagnosis += "📊 Latencias:\n"
        if stats['router_latency']:
            diagnosis += f"  • Router: {stats['router_latency']:.0f}ms\n"
        if stats['internet_latency']:
            diagnosis += f"  • Internet: {stats['internet_latency']:.0f}ms\n"
        diagnosis += f"  • Jitter: {stats['jitter']:.0f}ms\n\n"

        # Problemas
        if 'issues' in stats:
            diagnosis += "🔍 Diagnóstico:\n"
            for issue in stats['issues']:
                diagnosis += f"  {issue}\n"
            diagnosis += "\n"

        # Recomendaciones
        if 'recommendations' in stats and stats['recommendations']:
            diagnosis += "💡 Recomendaciones:\n"
            for rec in stats['recommendations']:
                diagnosis += f"  {rec}\n"

        return diagnosis

    def start_monitoring(self):
        """Iniciar monitoreo continuo en background"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Monitor de red iniciado")

    def stop_monitoring(self):
        """Detener monitoreo"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("✅ Monitor de red detenido")

    def _monitor_loop(self):
        """Loop de monitoreo en background"""
        while self.running:
            self.analyze_network_health()
            time.sleep(self.measure_interval)

    def get_latency_history(self, host: str = 'google_dns', minutes: int = 60) -> List[Dict]:
        """
        Obtener historial de latencia

        Args:
            host: Host a consultar
            minutes: Minutos de historial

        Returns:
            Lista de mediciones [{timestamp, latency}, ...]
        """
        if host not in self.latency_history:
            return []

        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        history = [
            entry for entry in self.latency_history[host]
            if entry['timestamp'] >= cutoff
        ]

        return history


def main():
    """Testing"""
    print("🛡️  IoT Sentry - Network Monitor Test")
    print("=" * 50)
    print()

    monitor = NetworkMonitor()

    print("📡 Midiendo latencias...\n")
    latencies = monitor.measure_all_latencies()

    for host, latency in latencies.items():
        if latency:
            print(f"  • {host:20} : {latency:6.1f} ms")
        else:
            print(f"  • {host:20} : TIMEOUT")

    print("\n🔍 Analizando salud de red...\n")
    health = monitor.analyze_network_health()

    print(monitor.get_diagnosis())

    print("✨ Test completado!")


if __name__ == "__main__":
    main()
