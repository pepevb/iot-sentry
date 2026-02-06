# Guía de Instalación - IoT Sentry

Esta guía detalla las diferentes opciones de instalación para IoT Sentry en cada plataforma.

## 📋 Requisitos Previos

### Todos los métodos
- Conexión a red local (WiFi o Ethernet)
- Al menos 1 dispositivo IoT conectado a la misma red

### Desde código fuente
- Python 3.10 o superior
- Node.js 18 o superior
- npm o yarn
- Git

### Docker
- Docker 24 o superior
- Docker Compose 2.2 o superior

---

## 🪟 Windows

### Opción 1: Ejecutable (Recomendado)

1. **Descargar** el ejecutable:
   ```
   IoTSentry-v1.0.0-Windows.exe
   ```

2. **Instalar dependencias** (solo primera vez):
   - Descargar e instalar [Npcap](https://npcap.com/#download)
   - Durante la instalación, marcar "Install Npcap in WinPcap API-compatible mode"

3. **Ejecutar como Administrador**:
   - Clic derecho en `IoTSentry.exe`
   - Seleccionar "Ejecutar como administrador"

4. **Permitir acceso** en el firewall si se solicita

### Opción 2: Desde código fuente

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/iot-sentry.git
cd iot-sentry

# 2. Instalar Npcap (ver arriba)

# 3. Crear entorno virtual Python
python -m venv venv
venv\Scripts\activate

# 4. Instalar dependencias Python
cd agent
pip install -r requirements.txt

# 5. Descargar bases de datos
cd ../scripts
bash download-geodata.sh  # Requiere Git Bash o WSL

# 6. Instalar dependencias del dashboard
cd ../dashboard
npm install

# 7. Compilar dashboard
npm run build

# 8. Ejecutar (como Administrador)
cd ../desktop
python app.py
```

---

## 🍎 macOS

### Opción 1: Ejecutable (Recomendado)

1. **Descargar** el archivo:
   ```
   IoTSentry-v1.0.0-macOS.dmg
   ```

2. **Montar e instalar**:
   - Doble clic en `.dmg`
   - Arrastrar `IoTSentry.app` a la carpeta Applications

3. **Primera ejecución**:
   ```bash
   sudo /Applications/IoTSentry.app/Contents/MacOS/IoTSentry
   ```
   - Introducir contraseña de administrador
   - macOS puede pedir permisos adicionales (permitirlos)

4. **Ejecuciones siguientes**:
   - Doble clic en la app (ya no requiere sudo si se configuró correctamente)

### Opción 2: Homebrew + Código fuente

```bash
# 1. Instalar dependencias
brew install python@3.11 node libpcap

# 2. Clonar repositorio
git clone https://github.com/tu-usuario/iot-sentry.git
cd iot-sentry

# 3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependencias Python
cd agent
pip install -r requirements.txt

# 5. Descargar bases de datos
cd ../scripts
./download-geodata.sh

# 6. Instalar dependencias del dashboard
cd ../dashboard
npm install

# 7. Compilar dashboard
npm run build

# 8. Ejecutar con sudo
cd ../desktop
sudo python app.py
```

### Solución de problemas macOS

**Error: "IoTSentry.app is damaged"**
```bash
sudo xattr -rd com.apple.quarantine /Applications/IoTSentry.app
```

**Error de permisos de red**
```bash
# Agregar terminal a "Full Disk Access" en:
# System Preferences > Security & Privacy > Privacy > Full Disk Access
```

---

## 🐧 Linux

### Opción 1: AppImage (Recomendado)

1. **Descargar** el AppImage:
   ```bash
   wget https://github.com/tu-usuario/iot-sentry/releases/download/v1.0.0/IoTSentry-v1.0.0-Linux.AppImage
   ```

2. **Dar permisos de ejecución**:
   ```bash
   chmod +x IoTSentry-v1.0.0-Linux.AppImage
   ```

3. **Configurar permisos de captura** (solo primera vez):
   ```bash
   # Opción A: Usar setcap (recomendado)
   sudo setcap cap_net_raw+ep IoTSentry-v1.0.0-Linux.AppImage

   # Opción B: Ejecutar con sudo
   sudo ./IoTSentry-v1.0.0-Linux.AppImage
   ```

4. **Ejecutar**:
   ```bash
   ./IoTSentry-v1.0.0-Linux.AppImage
   ```

### Opción 2: Desde código fuente (Ubuntu/Debian)

```bash
# 1. Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    libpcap-dev \
    tcpdump \
    nodejs \
    npm

# 2. Clonar repositorio
git clone https://github.com/tu-usuario/iot-sentry.git
cd iot-sentry

# 3. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependencias Python
cd agent
pip install -r requirements.txt

# 5. Descargar bases de datos
cd ../scripts
./download-geodata.sh

# 6. Instalar dependencias del dashboard
cd ../dashboard
npm install

# 7. Compilar dashboard
npm run build

# 8. Configurar permisos (primera vez)
cd ..
sudo setcap cap_net_raw+ep $(which python3)

# 9. Ejecutar
cd desktop
python app.py
```

### Fedora/RHEL

```bash
# Instalar dependencias
sudo dnf install -y \
    python3.10 \
    python3-pip \
    libpcap-devel \
    tcpdump \
    nodejs \
    npm

# Seguir pasos 2-9 de Ubuntu/Debian
```

### Arch Linux

```bash
# Instalar dependencias
sudo pacman -S python python-pip libpcap tcpdump nodejs npm

# Seguir pasos 2-9 de Ubuntu/Debian
```

---

## 🐳 Docker (Todas las plataformas)

### Requisitos previos

- Docker instalado y en ejecución
- Docker Compose instalado

### Instalación

1. **Clonar repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/iot-sentry.git
   cd iot-sentry
   ```

2. **Descargar bases de datos geográficas**:
   ```bash
   ./scripts/download-geodata.sh
   ```

3. **Compilar dashboard**:
   ```bash
   cd dashboard
   npm install
   npm run build
   cd ..
   ```

4. **Iniciar con Docker Compose**:
   ```bash
   docker-compose up -d
   ```

5. **Acceder al dashboard**:
   ```
   http://localhost:8000
   ```

### Comandos útiles

```bash
# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Reconstruir imagen
docker-compose up -d --build
```

### Nota sobre Docker

⚠️ **Importante**: El modo `network_mode: host` es necesario para que el container pueda escanear la red del host. Esto puede tener limitaciones en macOS y Windows (Docker Desktop usa una VM).

Para mejor compatibilidad en macOS/Windows, se recomienda usar los ejecutables nativos en lugar de Docker.

---

## 🔧 Verificación de la Instalación

Una vez instalado, verifica que todo funciona:

1. **Abrir la aplicación** - Debe mostrar ventana del dashboard
2. **Verificar escaneo** - En la página de dispositivos, debe aparecer al menos tu router
3. **Verificar captura** - Navegar a detalle de dispositivo y ver que se registran flujos
4. **Verificar mapa** - Abrir página de mapa y ver marcadores geográficos

## 🆘 Solución de Problemas

### "Permission denied" al capturar tráfico

**Linux:**
```bash
sudo setcap cap_net_raw+ep /path/to/executable
```

**macOS/Windows:**
Ejecutar como administrador/sudo

### No se detectan dispositivos

- Verificar que estés en la misma red que los dispositivos IoT
- Desactivar temporalmente VPN
- Verificar que el firewall no bloquee la aplicación
- Esperar 1-2 minutos para el primer escaneo

### Error "GeoLite2 database not found"

```bash
cd scripts
./download-geodata.sh
```

### Dashboard no carga

- Verificar que el puerto 8000 no esté en uso
- Revisar logs en consola
- Reiniciar la aplicación

---

## 📞 Soporte

Si encuentras problemas durante la instalación:

1. Revisar [FAQ](./FAQ.md)
2. Buscar en [Issues](https://github.com/tu-usuario/iot-sentry/issues)
3. Crear un nuevo issue con:
   - Sistema operativo y versión
   - Método de instalación usado
   - Mensaje de error completo
   - Logs de la aplicación

---

**Siguiente paso**: [Guía de Uso](./USER_GUIDE.md)
