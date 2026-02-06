# IoT Sentry 🛡️

**Auditoría de privacidad para dispositivos IoT - 100% Local y Privado**

IoT Sentry es una aplicación nativa de macOS que permite a usuarios no técnicos auditar la privacidad de sus dispositivos IoT, mostrando a qué servidores se conectan y dónde están ubicados geográficamente.

**Desarrollado por**: José Viña Bilbao
**Licencia**: Software libre y gratuito - 100% libre para descargar y utilizar

## ✨ Características

- 🔍 **Descubrimiento automático** de dispositivos IoT en tu red local
- 🌍 **Visualización geográfica** de destinos de conexión en mapa mundial
- 🚨 **Alertas inteligentes** para comportamientos sospechosos
- 📊 **Dashboard interactivo** con métricas en tiempo real
- 🔒 **100% privado** - todo funciona localmente, sin servicios cloud
- 💻 **Multiplataforma** - Windows, macOS y Linux

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Menu Bar      │  rumps (macOS)
│   (Interfaz)    │  Icono personalizado
└────────┬────────┘
         │
    ┌────▼────────────┐
    │  Dashboard      │  PyQt6
    │  (On-demand)    │  Ventana completa
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Python Engine   │
    ├─────────────────┤
    │ • Scanner       │  Descubrimiento de dispositivos
    │ • Sniffer       │  Captura de tráfico
    │ • Analyzer      │  Geolocalización y alertas
    │ • Database      │  SQLite local
    └─────────────────┘
```

## 🚀 Instalación y Uso

### macOS (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/josevinabibilbao/iot-sentry.git
cd iot-sentry

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar (requiere sudo para captura de red)
./RUN.sh
```

### Aplicación Empaquetada (.app)

```bash
# Crear aplicación nativa de macOS
./build_macos.sh

# Instalar
cp -r "dist/IoT Sentry.app" /Applications/

# Ejecutar
open /Applications/"IoT Sentry.app"
```

### Otras Plataformas (Windows/Linux)

```bash
# Ejecutar solo el dashboard (sin menu bar)
python main.py
```

Ver [MULTIPLATAFORMA.md](MULTIPLATAFORMA.md) para más información.

## 📋 Requisitos

### Sistemas
- **macOS** 10.13+ (High Sierra o superior) - Soporte completo
- **Windows** 10+ - Dashboard únicamente (sin menu bar)
- **Linux** - Dashboard únicamente (sin menu bar)

### Software
- Python 3.10 o superior
- Permisos de administrador (para captura de tráfico)

### Permisos en macOS
```bash
# La app requiere sudo para capturar tráfico de red
sudo ./RUN.sh

# Primera ejecución: macOS pedirá permisos adicionales
# → Permitir acceso a red
# → Permitir notificaciones
```

## 🎯 Uso

### Menu Bar
1. Busca el icono 🛡️ en tu menu bar (arriba a la derecha)
2. Click en el icono para ver:
   - Dispositivos detectados
   - Alertas activas
   - Latencia de red en tiempo real
3. Click en "Abrir Dashboard" para ver la interfaz completa

### Dashboard
- **Dispositivos**: Lista completa de dispositivos IoT en tu red
- **Alertas**: Notificaciones de comportamientos sospechosos
- **Rendimiento**: Gráficos de tráfico y latencia
- **Logs**: Registro de actividad en tiempo real

Ver [README_EJECUTAR.md](README_EJECUTAR.md) para guía completa de uso.

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Core | Python 3.10+ |
| Menu Bar | rumps (macOS) |
| GUI | PyQt6 |
| Network | Scapy 2.5+ + netifaces |
| Geolocalización | geoip2 + GeoLite2 |
| Base de datos | SQLite + SQLAlchemy |
| Iconos | SVG → PNG (cairosvg) |
| Empaquetado | py2app (macOS) |

## 📁 Estructura del Proyecto

```
/iot-sentry
├── menubar_main.py            # App principal (menu bar)
├── main.py                    # Alternativa (solo dashboard)
├── setup.py                   # Configuración de empaquetado
│
├── /core                      # Motor principal
│   └── iot_sentry_engine.py
├── /agent                     # Componentes de red
│   ├── /scanner               # Escaneo de dispositivos
│   ├── /sniffer               # Captura de tráfico
│   ├── /analyzer              # Geolocalización
│   ├── /monitor               # Monitoreo
│   └── /database              # Modelos SQLAlchemy
├── /gui                       # Interfaz PyQt6
│   ├── main_window.py
│   └── theme.py
├── /assets                    # Iconos (15 PNG)
├── /data                      # Base de datos SQLite
└── /docs                      # Documentación técnica
```

## 🔐 Privacidad y Seguridad

- ✅ **Todo es local**: Ningún dato sale de tu red
- ✅ **Solo metadatos**: No captura contenido de paquetes, solo IPs y puertos
- ✅ **HTTPS respetado**: No intenta descifrar tráfico cifrado
- ✅ **Open source**: Código auditable y transparente

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

**MIT License** - Software 100% libre y gratuito

Este software es completamente libre para:
- ✅ Usar personalmente o comercialmente
- ✅ Modificar y adaptar
- ✅ Distribuir y compartir
- ✅ Uso privado y público

Ver archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**José Viña Bilbao**

Desarrollador de software especializado en seguridad y privacidad.

## 🙏 Agradecimientos

- [MaxMind](https://www.maxmind.com) por GeoLite2 database
- [IEEE](https://standards.ieee.org/) por OUI database
- Comunidad open source por las librerías utilizadas

## 📚 Documentación

- [README_EJECUTAR.md](README_EJECUTAR.md) - Guía rápida de ejecución
- [EMPAQUETAR.md](EMPAQUETAR.md) - Crear aplicación .app
- [MULTIPLATAFORMA.md](MULTIPLATAFORMA.md) - Soporte Windows/Linux
- [ICONOS_DASHBOARD.md](ICONOS_DASHBOARD.md) - Sistema de iconos
- [RESUMEN_COMPLETO.md](RESUMEN_COMPLETO.md) - Vista general completa
- [DOCS_INDEX.md](DOCS_INDEX.md) - Índice de documentación

## 📞 Soporte

- 🐛 [Reportar bugs](https://github.com/josevinabibilbao/iot-sentry/issues)
- 💡 [Solicitar features](https://github.com/josevinabibilbao/iot-sentry/issues)
- 📖 [Documentación completa](./DOCS_INDEX.md)

---

**⚠️ Nota Legal**: IoT Sentry está diseñado para uso personal en tu propia red. Asegúrate de cumplir con las leyes locales sobre monitoreo de red.

**💡 Software Libre**: Este proyecto es 100% libre y gratuito. Puedes descargarlo, usarlo y modificarlo sin restricciones bajo la licencia MIT.
