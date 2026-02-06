#!/usr/bin/env python3
"""
IoT Sentry - Menu Bar App para macOS

Aplicación de menu bar que monitorea dispositivos IoT
y muestra dashboard PyQt6 cuando se necesita.
"""

import sys
import os
import rumps
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer

# Ajustar path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from core import IoTSentryEngine


class IoTSentryMenuBar(rumps.App):
    """
    Aplicación de menu bar para IoT Sentry
    """

    def __init__(self):
        # Obtener ruta del icono
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'shield.png')

        super().__init__(
            name="IoT Sentry",
            icon=icon_path,
            quit_button=None,  # Lo crearemos custom
            template=True  # Importante para que se vea bien en ambos temas de macOS
        )

        # Guardar rutas de iconos
        self.icon_normal = icon_path
        self.icon_alert = os.path.join(os.path.dirname(__file__), 'assets', 'shield_alert.png')

        # Estado
        self.dashboard_window = None
        self.qt_app = None
        self.engine = None
        self.stats = {
            'devices': 0,
            'alerts': 0,
            'flows': 0,
            'capture_running': False
        }

        # Crear menú
        self._create_menu()

        # Iniciar engine
        self._start_engine()

        # Timer para actualizar stats cada 5 segundos
        self.timer = rumps.Timer(self._update_stats, 5)
        self.timer.start()

    def _create_menu(self):
        """Crear estructura del menú"""
        self.menu = [
            rumps.MenuItem("Abrir Dashboard", callback=self.open_dashboard),
            rumps.separator,
            rumps.MenuItem("Dispositivos: 0", callback=None),
            rumps.MenuItem("Alertas: 0", callback=None),
            rumps.MenuItem("Lag: -", callback=None),
            rumps.separator,
            rumps.MenuItem("Escanear Red", callback=self.manual_scan),
            rumps.separator,
            rumps.MenuItem("Acerca de", callback=self.show_about),
            rumps.MenuItem("Salir", callback=self.quit_app)
        ]

    def _start_engine(self):
        """Iniciar el engine de IoT Sentry en background"""
        try:
            self.engine = IoTSentryEngine()

            # Configurar callbacks
            self.engine.set_device_found_callback(self._on_device_found)
            self.engine.set_alert_callback(self._on_alert)

            # Iniciar
            self.engine.start()

            rumps.notification(
                title="IoT Sentry",
                subtitle="Motor iniciado",
                message="Monitoreando tu red local..."
            )
        except Exception as e:
            rumps.notification(
                title="IoT Sentry - Error",
                subtitle="No se pudo iniciar",
                message=f"Error: {str(e)}\n\nEjecuta con: sudo python menubar_main.py"
            )

    def _update_stats(self, _):
        """Actualizar estadísticas en el menú"""
        if not self.engine:
            return

        try:
            self.stats = self.engine.get_stats()

            # Actualizar items del menú
            devices_count = self.stats.get('total_devices', 0)
            alerts_count = self.stats.get('unread_alerts', 0)

            # Obtener lag promedio
            avg_latency = self.stats.get('average_latency', None)
            if avg_latency is not None:
                lag_text = f"Lag: {avg_latency:.1f}ms"
            else:
                lag_text = "Lag: -"

            self.menu["Dispositivos: 0"].title = f"Dispositivos: {devices_count}"
            self.menu["Alertas: 0"].title = f"Alertas: {alerts_count}"
            self.menu["Lag: -"].title = lag_text

            # Cambiar icono según alertas
            if alerts_count > 0:
                self.icon = self.icon_alert  # Icono rojo con alerta
            else:
                self.icon = self.icon_normal  # Icono normal

        except Exception as e:
            print(f"Error actualizando stats: {e}")

    def _on_device_found(self, device):
        """Callback cuando se encuentra un dispositivo"""
        rumps.notification(
            title="Nuevo dispositivo detectado",
            subtitle=f"{device.vendor or 'Desconocido'}",
            message=f"IP: {device.ip_address}\nMAC: {device.mac_address}"
        )

    def _on_alert(self, alert):
        """Callback cuando hay una alerta"""
        rumps.notification(
            title=f"🚨 Alerta de Seguridad",
            subtitle=alert.alert_type,
            message=alert.message
        )

    @rumps.clicked("Abrir Dashboard")
    def open_dashboard(self, _):
        """Abrir ventana del dashboard PyQt6"""
        if self.dashboard_window and self.dashboard_window.isVisible():
            # Si ya está abierta, traerla al frente
            self.dashboard_window.activateWindow()
            self.dashboard_window.raise_()
        else:
            # Crear nueva ventana
            if not self.qt_app:
                # Crear QApplication si no existe
                self.qt_app = QApplication.instance()
                if not self.qt_app:
                    self.qt_app = QApplication(sys.argv)
                    self.qt_app.setApplicationName("IoT Sentry")
                    self.qt_app.setOrganizationName("IoT Sentry")

                    # Aplicar tema oscuro
                    self.qt_app.setStyle("Fusion")
                    from gui.theme import apply_dark_theme
                    apply_dark_theme(self.qt_app)

            # Crear ventana con el engine existente
            self.dashboard_window = MainWindow(engine=self.engine)
            self.dashboard_window.show()

    @rumps.clicked("Escanear Red")
    def manual_scan(self, _):
        """Escaneo manual de red"""
        rumps.notification(
            title="IoT Sentry",
            subtitle="Escaneando red",
            message="Buscando dispositivos..."
        )
        # El engine hará el escaneo automáticamente

    @rumps.clicked("Acerca de")
    def show_about(self, _):
        """Mostrar ventana Acerca de"""
        rumps.alert(
            title="IoT Sentry",
            message="Auditoría de privacidad para dispositivos IoT\n\n"
                   "100% Local y Privado\n"
                   "© 2026",
            ok="OK"
        )

    @rumps.clicked("Salir")
    def quit_app(self, _):
        """Salir de la aplicación"""
        # Detener engine
        if self.engine and self.engine.running:
            self.engine.stop()

        # Cerrar dashboard si está abierto
        if self.dashboard_window:
            self.dashboard_window.close()

        # Salir
        rumps.quit_application()


def main():
    """Punto de entrada de la aplicación"""
    # Verificar permisos
    if os.geteuid() != 0:
        print("⚠️  ADVERTENCIA: IoT Sentry necesita permisos de superusuario para capturar tráfico.")
        print("   Ejecuta con: sudo python menubar_main.py")
        print()

    # Iniciar app de menu bar
    app = IoTSentryMenuBar()
    app.run()


if __name__ == "__main__":
    main()
