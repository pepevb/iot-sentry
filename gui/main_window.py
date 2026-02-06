"""
IoT Sentry - Ventana Principal
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QStatusBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTextEdit
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QFont, QPixmap

from core import IoTSentryEngine


class MainWindow(QMainWindow):
    """
    Ventana principal de IoT Sentry
    """

    def __init__(self, engine=None):
        super().__init__()

        # Motor principal (usar el proporcionado o crear uno nuevo)
        self.engine = engine if engine is not None else IoTSentryEngine()
        self._owns_engine = engine is None  # Solo iniciamos/detenemos si lo creamos nosotros

        # Configurar ventana
        self.setWindowTitle("IoT Sentry - Auditoría de Privacidad IoT")
        self.setGeometry(100, 100, 1200, 800)

        # Cargar iconos
        self._load_icons()

        # Crear UI
        self._create_ui()

        # Configurar callbacks del engine
        self.engine.set_device_found_callback(self._on_device_found)
        self.engine.set_alert_callback(self._on_alert)

        # Timer para actualizar stats
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._update_stats)
        self.stats_timer.start(5000)  # Cada 5 segundos

        # Iniciar engine solo si lo creamos nosotros
        if self._owns_engine:
            self._start_engine()
        else:
            # Si usamos un engine externo, cargar datos iniciales
            self._refresh_devices()
            self._refresh_alerts()
            self._update_stats()

    def _load_icons(self):
        """Cargar iconos para usar en la UI"""
        # Directorio base (dos niveles arriba desde gui/)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, 'assets')

        # Cargar iconos de 64px para dashboard
        self.icons = {}
        icon_files = {
            'shield': 'shield_64.png',
            'shield_alert': 'shield_alert_64.png',
            'network': 'network_64.png',
            'signal': 'signal_64.png',
            'alert': 'alert_64.png',
            'radar': 'radar_64.png'
        }

        for key, filename in icon_files.items():
            icon_path = os.path.join(assets_dir, filename)
            if os.path.exists(icon_path):
                self.icons[key] = QIcon(icon_path)
            else:
                self.icons[key] = QIcon()  # Icono vacío como fallback

        # Cargar icono de ventana (128px)
        window_icon_path = os.path.join(assets_dir, 'shield_128.png')
        if os.path.exists(window_icon_path):
            self.setWindowIcon(QIcon(window_icon_path))

    def _create_ui(self):
        """
        Crear interfaz de usuario
        """
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)

        # Header con stats
        header = self._create_header()
        main_layout.addWidget(header)

        # Tabs principales
        tabs = QTabWidget()
        tabs.addTab(self._create_devices_tab(), self.icons.get('network', QIcon()), "Dispositivos")
        tabs.addTab(self._create_alerts_tab(), self.icons.get('alert', QIcon()), "Alertas")
        tabs.addTab(self._create_performance_tab(), self.icons.get('signal', QIcon()), "Rendimiento")
        tabs.addTab(self._create_logs_tab(), QIcon(), "Logs")

        main_layout.addWidget(tabs)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Iniciando...")

    def _create_header(self) -> QWidget:
        """
        Crear header con estadísticas

        Returns:
            Widget del header
        """
        header = QWidget()
        layout = QHBoxLayout(header)

        # Stats cards
        self.stats_labels = {}

        stats = [
            ('devices', 'Dispositivos', '0', 'network'),
            ('alerts', 'Alertas', '0', 'alert'),
            ('flows', 'Flujos', '0', 'signal'),
            ('capture', 'Captura', 'Detenida', 'radar')
        ]

        for key, title, initial_value, icon_key in stats:
            icon = self.icons.get(icon_key, QIcon())
            card = self._create_stat_card(title, initial_value, icon)
            self.stats_labels[key] = card['value']
            layout.addWidget(card['widget'])

        # Botón de control
        self.start_stop_btn = QPushButton("⏸️ Detener")
        self.start_stop_btn.clicked.connect(self._toggle_engine)
        layout.addWidget(self.start_stop_btn)

        return header

    def _create_stat_card(self, title: str, value: str, icon: QIcon = None) -> dict:
        """
        Crear tarjeta de estadística

        Args:
            title: Título de la stat
            value: Valor inicial
            icon: Icono opcional

        Returns:
            Dict con 'widget' y 'value' label
        """
        card = QWidget()
        card.setMinimumWidth(150)
        layout = QVBoxLayout(card)

        # Icono (si se proporciona)
        if icon and not icon.isNull():
            icon_label = QLabel()
            pixmap = icon.pixmap(32, 32)  # Tamaño del icono
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        title_label.setFont(font)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_value = QFont()
        font_value.setPointSize(16)
        font_value.setBold(True)
        value_label.setFont(font_value)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return {'widget': card, 'value': value_label}

    def _create_devices_tab(self) -> QWidget:
        """
        Crear tab de dispositivos

        Returns:
            Widget del tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Botón de escaneo manual
        scan_btn = QPushButton("🔍 Escanear Red Ahora")
        scan_btn.clicked.connect(self._manual_scan)
        layout.addWidget(scan_btn)

        # Tabla de dispositivos
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(7)
        self.devices_table.setHorizontalHeaderLabels([
            "Icono", "IP", "MAC", "Fabricante", "Tipo", "Hostname", "Última Conexión"
        ])

        # Ajustar columnas
        header = self.devices_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Icono
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # IP
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # MAC
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Fabricante
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Tipo
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Hostname
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Última Conexión

        layout.addWidget(self.devices_table)

        return widget

    def _create_alerts_tab(self) -> QWidget:
        """
        Crear tab de alertas

        Returns:
            Widget del tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Tabla de alertas
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels([
            "Severidad", "Tipo", "Mensaje", "Dispositivo", "Timestamp"
        ])

        header = self.alerts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.alerts_table)

        return widget

    def _create_performance_tab(self) -> QWidget:
        """
        Crear tab de rendimiento

        Returns:
            Widget del tab
        """
        from gui.performance_tab import PerformanceTab
        return PerformanceTab(self.engine)

    def _create_logs_tab(self) -> QWidget:
        """
        Crear tab de logs

        Returns:
            Widget del tab
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        layout.addWidget(self.logs_text)

        return widget

    def _start_engine(self):
        """
        Iniciar motor de IoT Sentry
        """
        try:
            self.engine.start()
            self.statusBar.showMessage("✅ Motor iniciado correctamente")
            self._log("✅ IoT Sentry iniciado")
            self._refresh_devices()
            self._refresh_alerts()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error iniciando motor:\n{str(e)}\n\n"
                "Asegúrate de ejecutar con permisos de administrador."
            )
            self.statusBar.showMessage(f"❌ Error: {str(e)}")

    def _toggle_engine(self):
        """
        Alternar motor (iniciar/detener)
        """
        if self.engine.running:
            self.engine.stop()
            self.start_stop_btn.setText("▶️ Iniciar")
            self._log("⏸️ Motor detenido")
        else:
            self._start_engine()
            self.start_stop_btn.setText("⏸️ Detener")

    def _manual_scan(self):
        """
        Escaneo manual de red
        """
        self._log("🔍 Iniciando escaneo manual...")
        self.statusBar.showMessage("Escaneando red...")
        # El engine hará el escaneo automáticamente
        QTimer.singleShot(3000, self._refresh_devices)

    def _refresh_devices(self):
        """
        Refrescar tabla de dispositivos
        """
        devices = self.engine.get_devices()

        self.devices_table.setRowCount(len(devices))

        for row, device in enumerate(devices):
            # Obtener icono desde el identifier
            device_info = self.engine.identifier.identify_device(
                device.mac_address,
                device.hostname
            )

            # Columnas: Icono, IP, MAC, Fabricante, Tipo, Hostname, Última Conexión
            self.devices_table.setItem(row, 0, QTableWidgetItem(device_info['icon']))
            self.devices_table.setItem(row, 1, QTableWidgetItem(device.ip_address or "N/A"))
            self.devices_table.setItem(row, 2, QTableWidgetItem(device.mac_address))
            self.devices_table.setItem(row, 3, QTableWidgetItem(device.vendor or "Unknown"))
            self.devices_table.setItem(row, 4, QTableWidgetItem(device_info['display_name']))
            self.devices_table.setItem(row, 5, QTableWidgetItem(device.hostname or "N/A"))
            self.devices_table.setItem(row, 6, QTableWidgetItem(
                device.last_seen.strftime("%Y-%m-%d %H:%M:%S") if device.last_seen else "N/A"
            ))

    def _refresh_alerts(self):
        """
        Refrescar tabla de alertas
        """
        alerts = self.engine.get_alerts()

        self.alerts_table.setRowCount(len(alerts))

        for row, alert in enumerate(alerts):
            # Severidad con color
            severity_item = QTableWidgetItem(alert.severity.upper())
            from gui.theme import SEVERITY_COLORS
            severity_item.setForeground(Qt.GlobalColor.white)
            # TODO: Agregar color de fondo

            self.alerts_table.setItem(row, 0, severity_item)
            self.alerts_table.setItem(row, 1, QTableWidgetItem(alert.alert_type))
            self.alerts_table.setItem(row, 2, QTableWidgetItem(alert.message))
            self.alerts_table.setItem(row, 3, QTableWidgetItem(str(alert.device_id)))
            self.alerts_table.setItem(row, 4, QTableWidgetItem(
                alert.timestamp.strftime("%Y-%m-%d %H:%M:%S") if alert.timestamp else "N/A"
            ))

    def _update_stats(self):
        """
        Actualizar estadísticas en header
        """
        stats = self.engine.get_stats()

        self.stats_labels['devices'].setText(str(stats.get('total_devices', 0)))
        self.stats_labels['alerts'].setText(str(stats.get('unread_alerts', 0)))
        self.stats_labels['flows'].setText(str(stats.get('active_flows', 0)))

        capture_status = "✅ Activa" if stats.get('capture_running', False) else "⏸️ Detenida"
        self.stats_labels['capture'].setText(capture_status)

    def _on_device_found(self, device):
        """
        Callback cuando se encuentra un nuevo dispositivo

        Args:
            device: Dispositivo encontrado
        """
        self._log(f"📱 Nuevo dispositivo: {device.vendor} ({device.ip_address})")
        self._refresh_devices()

    def _on_alert(self, alert):
        """
        Callback cuando se genera una alerta

        Args:
            alert: Alerta generada
        """
        self._log(f"🚨 ALERTA [{alert.severity.upper()}]: {alert.message}")
        self._refresh_alerts()

        # Notificación visual
        self.statusBar.showMessage(f"⚠️ Nueva alerta: {alert.message}", 5000)

    def _log(self, message: str):
        """
        Agregar mensaje al log

        Args:
            message: Mensaje a logear
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_text.append(f"[{timestamp}] {message}")

    def closeEvent(self, event):
        """
        Manejar cierre de ventana

        Args:
            event: Evento de cierre
        """
        # Detener engine solo si lo creamos nosotros
        if self._owns_engine and self.engine.running:
            self.engine.stop()

        event.accept()
