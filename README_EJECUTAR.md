# 🚀 Cómo Ejecutar IoT Sentry Menu Bar

## Ejecución Rápida

```bash
cd ~/iot-sentry
./RUN.sh
```

**¡Eso es todo!**

Busca el icono 🛡️ en tu menu bar (arriba a la derecha).

---

## ¿Qué verás?

### 1. En el Menu Bar
Un icono de escudo con señal WiFi: **[🛡️]**

### 2. Al hacer click
```
Abrir Dashboard
─────────────────
Dispositivos: 3
Alertas: 0
Lag: 11.4ms
─────────────────
Escanear Red
─────────────────
Acerca de
Salir
```

### 3. Al hacer click en "Abrir Dashboard"
Se abre una ventana completa con:
- Tabla de dispositivos
- Alertas de seguridad
- Gráficos de rendimiento
- Logs en tiempo real

---

## Con captura de red completa

Si quieres capturar tráfico de red (requiere permisos):

```bash
sudo ./RUN.sh
```

Te pedirá tu contraseña.

---

## Verificar antes de ejecutar

```bash
# Test rápido
python test_menubar.py

# Test de latencia
python test_lag.py
```

---

## Si algo no funciona

### "No veo el icono en el menu bar"

1. Verifica que la app esté corriendo (mira la terminal)
2. Busca en el área de "overflow" (los tres puntitos →)
3. Revisa Preferencias → Seguridad → Privacidad

### "Error: No such file or directory"

```bash
# Verifica que estás en el directorio correcto
pwd
# Debería mostrar: ~/iot-sentry

# Si no, navega:
cd ~/iot-sentry
```

### "Operation not permitted"

```bash
# Ejecuta con sudo
sudo ./RUN.sh
```

---

## Detener la aplicación

**Desde el menú:**
Click en el icono → Salir

**Desde la terminal:**
`Ctrl + C`

---

## Archivos Principales

| Archivo | Descripción |
|---------|-------------|
| `RUN.sh` | Script principal de ejecución |
| `menubar_main.py` | Código de la app |
| `assets/shield.png` | Icono normal |
| `assets/shield_alert.png` | Icono con alerta |

---

## Documentación Completa

- **[RESUMEN_FINAL.md](RESUMEN_FINAL.md)** - Resumen completo
- **[ICONOS.md](ICONOS.md)** - Detalles de los iconos
- **[MENU_MINIMALISTA.md](MENU_MINIMALISTA.md)** - Diseño del menú
- **[QUICK_START_MENUBAR.md](QUICK_START_MENUBAR.md)** - Guía rápida

---

**¡Disfruta de tu monitor de IoT!** 🛡️
