# 🌍 IoT Sentry - Soporte Multiplataforma

## ❓ ¿Funciona en Windows y Linux?

### Respuesta Corta
**Parcialmente** - Con limitaciones importantes.

### Respuesta Detallada

#### ✅ Lo que SÍ funciona en todas las plataformas:

| Componente | Windows | Linux | macOS |
|------------|---------|-------|-------|
| Core Engine | ✅ | ✅ | ✅ |
| Scanner de red | ✅ | ✅ | ✅ |
| Sniffer (Scapy) | ✅ | ✅ | ✅ |
| Base de datos | ✅ | ✅ | ✅ |
| Dashboard PyQt6 | ✅ | ✅ | ✅ |
| Geolocalización | ✅ | ✅ | ✅ |

#### ❌ Lo que NO funciona en otras plataformas:

| Componente | Windows | Linux | macOS |
|------------|---------|-------|-------|
| **Menu Bar (rumps)** | ❌ | ❌ | ✅ |
| App nativa .app | ❌ | ❌ | ✅ |

---

## 🔍 Explicación Técnica

### rumps (Menu Bar)
```python
import rumps  # ❌ Solo macOS
```

**Por qué no funciona**:
- rumps usa APIs específicas de macOS (Cocoa/AppKit)
- No tiene equivalente directo en Windows/Linux
- Es exclusivo para el sistema de menu bar de macOS

### Alternativas para Windows/Linux:

#### Windows
- **pystray** - System tray (bandeja del sistema)
- Icono junto al reloj
- Similar pero no idéntico

#### Linux
- **pystray** - System tray
- **AppIndicator** - Indicadores de aplicación
- Depende del entorno de escritorio (GNOME, KDE, etc.)

---

## 🎯 Estrategias Multiplataforma

### Opción 1: Solo Dashboard (Recomendado para cross-platform)

Usar **solo** la ventana PyQt6 sin menu bar:

```bash
# En cualquier plataforma
python main.py
```

**Ventajas**:
- ✅ Funciona en Windows, Linux y macOS
- ✅ Misma experiencia visual
- ✅ Todas las funcionalidades

**Desventajas**:
- ❌ Sin icono en menu bar/tray
- ❌ Ventana siempre visible

---

### Opción 2: Código Condicional

Detectar plataforma y adaptar:

```python
import platform

if platform.system() == 'Darwin':  # macOS
    from menubar_main import IoTSentryMenuBar
    app = IoTSentryMenuBar()
elif platform.system() == 'Windows':
    # Usar pystray para system tray
    pass
elif platform.system() == 'Linux':
    # Usar AppIndicator
    pass
else:
    # Fallback a PyQt6 puro
    from main import main
    main()
```

---

### Opción 3: pystray (Alternativa Multiplataforma)

Reescribir usando **pystray** en lugar de rumps:

```python
# Funciona en Windows, Linux y macOS
import pystray
from PIL import Image

# System tray en lugar de menu bar
icon = pystray.Icon("IoT Sentry")
```

**Pros**:
- ✅ Multiplataforma real
- ✅ Similar a menu bar

**Contras**:
- ⚠️ Menos nativo en macOS
- ⚠️ Requiere reescribir código

---

## 📦 Empaquetado por Plataforma

### macOS
```bash
# Usar py2app
./build_macos.sh

# Resultado: IoT Sentry.app
```

**Características**:
- ✅ Aplicación .app nativa
- ✅ Icono en menu bar
- ✅ Instalable en /Applications
- ✅ LSUIElement=True (sin icono en Dock)

---

### Windows
```bash
# Usar PyInstaller
pip install pyinstaller

# Crear ejecutable
pyinstaller --onefile \
            --windowed \
            --icon=assets/shield.ico \
            --name="IoT Sentry" \
            main.py

# Resultado: IoT Sentry.exe
```

**Características**:
- ✅ Ejecutable .exe
- ✅ Ventana PyQt6
- ❌ Sin system tray (a menos que uses pystray)

---

### Linux
```bash
# Usar PyInstaller o crear AppImage
pyinstaller --onefile \
            --windowed \
            --name="iot-sentry" \
            main.py

# O crear .deb package
# O usar snapcraft para Snap
```

**Características**:
- ✅ Ejecutable Linux
- ✅ Ventana PyQt6
- ❌ Sin app indicator (a menos que uses pystray/AppIndicator)

---

## 🎨 Comparación Visual

### macOS (Actual)
```
Menu Bar: [🛡️] ← Click aquí
          ├─ Abrir Dashboard
          ├─ Dispositivos: 3
          └─ ...

Dashboard: Ventana PyQt6 on-demand
```

### Windows (con pystray)
```
System Tray: 🛡️ (junto al reloj)
             ├─ Abrir Dashboard
             ├─ Dispositivos: 3
             └─ ...

Dashboard: Ventana PyQt6 on-demand
```

### Linux (con AppIndicator)
```
Indicator: 🛡️ (barra superior)
           ├─ Abrir Dashboard
           ├─ Dispositivos: 3
           └─ ...

Dashboard: Ventana PyQt6 on-demand
```

### Cualquier plataforma (solo PyQt6)
```
Ventana PyQt6 siempre visible
[Minimizar] [Maximizar] [Cerrar]
┌─────────────────────────┐
│ IoT Sentry              │
│ ───────────────────────│
│ [Stats] [Devices] ...  │
└─────────────────────────┘
```

---

## 💡 Recomendaciones

### Para usuarios de macOS:
✅ **Usar versión actual** con rumps
- Experiencia óptima
- Menu bar nativo
- App empaquetada (.app)

### Para usuarios de Windows/Linux:
✅ **Usar versión Dashboard pura** (main.py)
- Funcionalidad completa
- Sin complicaciones
- Una ventana PyQt6

### Para desarrollo multiplataforma:
⚠️ **Considerar migrar a pystray**
- Sistema tray en todas las plataformas
- Código unificado
- Más mantenimiento

---

## 🔧 Estado Actual del Proyecto

### ✅ Implementado
- Menu bar para **macOS** (rumps)
- Dashboard PyQt6 para **todas las plataformas**
- Engine Python para **todas las plataformas**

### ⚠️ Limitaciones Conocidas

| Plataforma | Limitación | Solución |
|------------|------------|----------|
| Windows | Sin menu bar | Usar main.py o implementar pystray |
| Linux | Sin menu bar | Usar main.py o implementar AppIndicator |
| macOS | Requiere sudo | Normal para captura de red |

---

## 📋 Archivos de Ejecución

### macOS
```bash
./RUN.sh                  # Menu bar version
python main.py            # Dashboard only
./build_macos.sh          # Create .app
```

### Windows
```bash
python main.py            # Dashboard only
# TODO: build_windows.bat
```

### Linux
```bash
python main.py            # Dashboard only
# TODO: build_linux.sh
```

---

## 🚀 Próximos Pasos (Multiplataforma)

### Prioridad Alta
- [ ] Script `build_windows.bat` para PyInstaller
- [ ] Script `build_linux.sh` para AppImage
- [ ] Documentación específica por plataforma

### Prioridad Media
- [ ] Implementar pystray como alternativa
- [ ] Código condicional por plataforma
- [ ] Iconos .ico para Windows

### Prioridad Baja
- [ ] Instaladores (.msi, .deb, .rpm)
- [ ] Auto-updater
- [ ] Firma de código

---

## 📊 Tabla Resumen

| Característica | macOS | Windows | Linux |
|----------------|-------|---------|-------|
| **Menu Bar** | ✅ rumps | ❌ No disponible | ❌ No disponible |
| **System Tray** | ⚠️ Posible con pystray | ⚠️ Posible con pystray | ⚠️ Posible con pystray |
| **Dashboard** | ✅ PyQt6 | ✅ PyQt6 | ✅ PyQt6 |
| **Scanner** | ✅ | ✅ | ✅ |
| **Sniffer** | ✅ | ✅ (requiere permisos) | ✅ (requiere permisos) |
| **Packaging** | ✅ .app | ⚠️ .exe | ⚠️ AppImage |
| **Estado** | ✅ Completo | ⚠️ Parcial | ⚠️ Parcial |

---

## 🎯 Conclusión

**Estado actual**: Aplicación **optimizada para macOS** con menu bar nativo.

**Compatibilidad**: El core funciona en todas las plataformas, pero la interfaz de menu bar es exclusiva de macOS.

**Para usuarios de Windows/Linux**: Usar `python main.py` para acceder a todas las funcionalidades mediante el dashboard PyQt6.

**Para verdadera multiplataforma**: Considerar migración futura a pystray o mantener dos versiones (menu bar para macOS, dashboard para otros).

---

**La versión actual es una app nativa de macOS con soporte experimental en otras plataformas** 🍎
