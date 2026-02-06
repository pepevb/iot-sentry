"""
IoT Sentry - Tab de Rendimiento

Muestra gráficos de tráfico y detector de LAG
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QGroupBox, QProgressBar
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from datetime import datetime, timedelta


class PerformanceTab(QWidget):
    """Tab de rendimiento con gráficos y diagnóstico"""

    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        # Inicializar componentes de monitoreo
        from agent.monitor import NetworkMonitor, BandwidthAnalyzer

        self.network_monitor = NetworkMonitor()

        # Obtener sesión de DB correctamente
        if hasattr(engine, 'db_session') and engine.db_session:
            self.bandwidth_analyzer = BandwidthAnalyzer(engine.db_session)
        else:
            # Crear nueva sesión si no existe
            from agent.database import SessionLocal
            self.bandwidth_analyzer = BandwidthAnalyzer(SessionLocal())

        # Configurar gateway
        net_info = engine.scanner.get_local_network_info()
        gateway = net_info.get('ip', '192.168.1.1').rsplit('.', 1)[0] + '.1'
        self.network_monitor.set_router_ip(gateway)

        # Iniciar monitoreo
        self.network_monitor.start_monitoring()

        # Crear UI
        self._create_ui()

        # Timers para actualización
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_displays)
        self.update_timer.start(10000)  # Cada 10 segundos

        # Actualización inicial
        self._update_displays()

    def _create_ui(self):
        """Crear interfaz de usuario"""
        layout = QVBoxLayout(self)

        # Sección superior: Diagnóstico de LAG
        lag_group = self._create_lag_section()
        layout.addWidget(lag_group)

        # Sección media: Vampiros de ancho de banda
        vampires_group = self._create_vampires_section()
        layout.addWidget(vampires_group)

        # Sección inferior: Gráfico de tráfico
        graph_group = self._create_graph_section()
        layout.addWidget(graph_group)

    def _create_lag_section(self) -> QGroupBox:
        """Crear sección de diagnóstico de LAG"""
        group = QGroupBox("🔍 Diagnóstico de Red y LAG")
        layout = QVBoxLayout(group)

        # Botón de análisis manual
        analyze_btn = QPushButton("🔄 Analizar Ahora")
        analyze_btn.clicked.connect(self._analyze_network)
        layout.addWidget(analyze_btn)

        # Estado general con icono grande
        status_layout = QHBoxLayout()

        self.status_label = QLabel("⚪ Analizando...")
        status_font = QFont()
        status_font.setPointSize(16)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Métricas de latencia
        metrics_layout = QHBoxLayout()

        self.router_latency_label = QLabel("Router: -- ms")
        self.internet_latency_label = QLabel("Internet: -- ms")
        self.jitter_label = QLabel("Jitter: -- ms")

        metrics_layout.addWidget(self.router_latency_label)
        metrics_layout.addWidget(self.internet_latency_label)
        metrics_layout.addWidget(self.jitter_label)

        layout.addLayout(metrics_layout)

        # Diagnóstico textual
        self.diagnosis_text = QTextEdit()
        self.diagnosis_text.setReadOnly(True)
        self.diagnosis_text.setMaximumHeight(150)
        layout.addWidget(self.diagnosis_text)

        return group

    def _create_vampires_section(self) -> QGroupBox:
        """Crear sección de vampiros de ancho de banda"""
        group = QGroupBox("🧛 Vampiros de Ancho de Banda")
        layout = QVBoxLayout(group)

        # Selector de período
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Análisis de:"))

        self.period_combo = QComboBox()
        self.period_combo.addItems(["Última hora", "Últimas 6 horas", "Últimas 24 horas"])
        self.period_combo.currentIndexChanged.connect(self._update_vampires)
        period_layout.addWidget(self.period_combo)

        period_layout.addStretch()
        layout.addLayout(period_layout)

        # Lista de vampiros
        self.vampires_text = QTextEdit()
        self.vampires_text.setReadOnly(True)
        self.vampires_text.setMaximumHeight(150)
        layout.addWidget(self.vampires_text)

        return group

    def _create_graph_section(self) -> QGroupBox:
        """Crear sección de gráfico de tráfico"""
        group = QGroupBox("📊 Tráfico de Red (últimas 24 horas)")
        layout = QVBoxLayout(group)

        # Selector de dispositivo
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Mostrar:"))

        self.device_combo = QComboBox()
        self.device_combo.addItem("Todos los dispositivos", None)
        self.device_combo.currentIndexChanged.connect(self._update_graph)
        device_layout.addWidget(self.device_combo)

        device_layout.addStretch()
        layout.addLayout(device_layout)

        # Gráfico
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground('w')
        self.graph_widget.setLabel('left', 'Mbps')
        self.graph_widget.setLabel('bottom', 'Tiempo')
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)

        layout.addWidget(self.graph_widget)

        return group

    def _analyze_network(self):
        """Analizar red manualmente"""
        self.status_label.setText("⚪ Analizando...")
        self.diagnosis_text.setText("Midiendo latencias...")

        # Análisis se hace en thread de monitoreo, solo forzamos actualización
        stats = self.network_monitor.analyze_network_health()
        self._update_lag_display(stats)

    def _update_displays(self):
        """Actualizar todas las visualizaciones"""
        self._update_lag_display()
        self._update_vampires()
        self._update_graph()
        self._update_device_list()

    def _update_lag_display(self, stats=None):
        """Actualizar display de diagnóstico de LAG"""
        if stats is None:
            stats = self.network_monitor.current_stats

        # Actualizar estado
        status_emojis = {
            'excellent': '🟢 EXCELENTE',
            'good': '🟢 BUENA',
            'fair': '🟡 ACEPTABLE',
            'poor': '🟠 MALA',
            'critical': '🔴 CRÍTICA',
            'unknown': '⚪ ANALIZANDO'
        }

        self.status_label.setText(status_emojis.get(stats['status'], '⚪ ANALIZANDO'))

        # Actualizar métricas
        if stats['router_latency']:
            self.router_latency_label.setText(f"Router: {stats['router_latency']:.0f} ms")
        else:
            self.router_latency_label.setText("Router: -- ms")

        if stats['internet_latency']:
            self.internet_latency_label.setText(f"Internet: {stats['internet_latency']:.0f} ms")
        else:
            self.internet_latency_label.setText("Internet: -- ms")

        self.jitter_label.setText(f"Jitter: {stats['jitter']:.0f} ms")

        # Actualizar diagnóstico
        diagnosis = self.network_monitor.get_diagnosis()
        self.diagnosis_text.setText(diagnosis)

    def _update_vampires(self):
        """Actualizar lista de vampiros de ancho de banda"""
        try:
            # Obtener período seleccionado
            period_map = {0: 1, 1: 6, 2: 24}
            hours = period_map.get(self.period_combo.currentIndex(), 1)

            # Obtener vampiros
            vampires = self.bandwidth_analyzer.detect_bandwidth_hogs(hours, threshold_percentage=15.0)
        except Exception as e:
            # Si hay error (ej. no hay datos), mostrar mensaje amigable
            self.vampires_text.setText(f"ℹ️  Recopilando datos...\n\nAún no hay suficientes datos de tráfico.\nDeja la aplicación funcionando unos minutos.")
            return

        if not vampires:
            # Verificar si hay datos
            try:
                devices = self.bandwidth_analyzer.get_bandwidth_by_device(hours)
                total_bytes = sum(d['bytes_sent'] for d in devices)

                if total_bytes < 1000:  # Menos de 1KB = no hay datos
                    self.vampires_text.setText(
                        "ℹ️  Recopilando datos de tráfico...\n\n"
                        "La aplicación necesita capturar tráfico de red durante unos minutos.\n\n"
                        "Usa algunos dispositivos IoT (navega en tu móvil, pídele algo a Alexa, etc.) "
                        "y los datos empezarán a aparecer."
                    )
                else:
                    self.vampires_text.setText(
                        "✅ No se detectaron vampiros de ancho de banda\n\n"
                        f"Tráfico total en últimas {hours}h: {total_bytes / (1024**2):.1f} MB\n\n"
                        "Todos los dispositivos tienen consumo normal."
                    )
            except:
                self.vampires_text.setText("✅ No se detectaron vampiros de ancho de banda")
            return

        # Generar texto
        text = f"⚠️  {len(vampires)} vampiro(s) detectado(s):\n\n"

        for vamp in vampires:
            text += f"{vamp['emoji']} {vamp['hostname']}\n"
            text += f"   Consumo: {vamp['percentage']:.0f}% del total ({vamp['mbps_avg']:.1f} Mbps promedio)\n"
            text += f"   Total: {vamp['bytes_sent'] / (1024**2):.1f} MB en {hours}h\n\n"

        text += "💡 Recomendaciones:\n"
        text += "• Pausar streaming de video durante videollamadas importantes\n"
        text += "• Programar backups/actualizaciones para horarios nocturnos\n"
        text += "• Considerar limitar ancho de banda de dispositivos específicos en el router"

        self.vampires_text.setText(text)

    def _update_graph(self):
        """Actualizar gráfico de tráfico"""
        try:
            # Obtener dispositivo seleccionado
            device_id = self.device_combo.currentData()

            # Obtener timeline
            timeline = self.bandwidth_analyzer.get_traffic_timeline(device_id, hours=24)
        except Exception as e:
            # Si hay error, mostrar gráfico vacío
            self.graph_widget.clear()
            return

        if not timeline:
            self.graph_widget.clear()
            self.graph_widget.plot([0], [0])
            return

        # Preparar datos para gráfico
        timestamps = [(t['timestamp'] - timeline[0]['timestamp']).total_seconds() / 3600 for t in timeline]
        mbps_values = [t['mbps'] for t in timeline]

        # Limpiar y graficar
        self.graph_widget.clear()
        self.graph_widget.plot(
            timestamps,
            mbps_values,
            pen=pg.mkPen(color='#2a82da', width=2),
            fillLevel=0,
            fillBrush=(42, 130, 218, 50)
        )

    def _update_device_list(self):
        """Actualizar lista de dispositivos en combo"""
        current_device = self.device_combo.currentData()

        # Limpiar y recargar
        self.device_combo.clear()
        self.device_combo.addItem("Todos los dispositivos", None)

        # Obtener dispositivos
        devices = self.engine.get_devices()
        for device in devices:
            name = device.hostname or device.ip_address or device.mac_address
            self.device_combo.addItem(name, device.id)

        # Restaurar selección si es posible
        if current_device:
            index = self.device_combo.findData(current_device)
            if index >= 0:
                self.device_combo.setCurrentIndex(index)

    def closeEvent(self, event):
        """Manejar cierre del tab"""
        self.network_monitor.stop_monitoring()
        event.accept()
