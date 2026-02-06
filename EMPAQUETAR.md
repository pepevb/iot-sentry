# 📦 Empaquetar IoT Sentry como App de macOS

## 🚀 Proceso Rápido

```bash
# 1. Ejecutar script de build
./build_macos.sh

# 2. Resultado
# dist/IoT Sentry.app
```

**¡Eso es todo!**

---

## 📋 Requisitos

### Antes de empaquetar:

1. **Python 3.10+** instalado
2. **Virtualenv** activado con todas las dependencias
3. **py2app** instalado:
   ```bash
   pip install py2app
   ```

---

## 🔧 Proceso Detallado

### 1. Preparación

```bash
cd ~/iot-sentry
source venv/bin/activate
pip install py2app
```

### 2. Construcción

```bash
# Opción A: Usar script
./build_macos.sh

# Opción B: Manual
python setup.py py2app
```

### 3. Resultado

```
dist/
└── IoT Sentry.app/
    ├── Contents/
    │   ├── Info.plist          # Metadata
    │   ├── MacOS/
    │   │   └── IoT Sentry      # Ejecutable
    │   ├── Resources/
    │   │   ├── assets/         # Iconos
    │   │   ├── data/           # Base de datos
    │   │   └── ...
    │   └── Frameworks/         # Python + dependencias
    └── ...
```

---

## 🎯 Características de la App

### Metadata (Info.plist)

```xml
<key>CFBundleName</key>
<string>IoT Sentry</string>

<key>CFBundleIdentifier</key>
<string>com.iotsentry.app</string>

<key>CFBundleVersion</key>
<string>1.0.0</string>

<key>LSUIElement</key>
<true/>  <!-- ⚠️ Importante: App de menu bar -->
```

**LSUIElement=True** significa:
- ✅ Aparece en menu bar
- ✅ **NO** aparece en Dock
- ✅ **NO** aparece en Cmd+Tab
- ✅ Comportamiento típico de app de menu bar

---

## 📦 Tamaño de la App

### Componentes incluidos:

| Componente | Tamaño aprox. |
|------------|---------------|
| Python runtime | ~40 MB |
| PyQt6 | ~80 MB |
| Scapy + deps | ~10 MB |
| Tu código | ~1 MB |
| Assets (iconos) | ~0.05 MB |
| **Total** | **~130 MB** |

**Nota**: Es normal que sea grande porque incluye el runtime completo de Python.

---

## 🔍 Verificar la App

### Test 1: Estructura
```bash
# Ver contenido
ls -R "dist/IoT Sentry.app"

# Ver tamaño
du -sh "dist/IoT Sentry.app"
```

### Test 2: Ejecutar
```bash
# Desde terminal (para ver logs)
open "dist/IoT Sentry.app"

# O hacer doble click en Finder
```

### Test 3: Verificar permisos
```bash
# La app debe pedir permisos de red
# macOS mostrará diálogos la primera vez
```

---

## 💾 Instalación

### Método 1: Copiar a /Applications
```bash
# Copiar app
cp -r "dist/IoT Sentry.app" /Applications/

# Ejecutar
open /Applications/"IoT Sentry.app"
```

### Método 2: Crear DMG (Recomendado)

```bash
# Crear imagen de disco
hdiutil create -volname "IoT Sentry" \
               -srcfolder "dist/IoT Sentry.app" \
               -ov -format UDZO \
               "IoT Sentry-v1.0.0.dmg"
```

**Ventajas del DMG**:
- ✅ Fácil de distribuir
- ✅ Usuario arrastra a /Applications
- ✅ Aspecto profesional

---

## ⚠️ Permisos y Seguridad

### Primera Ejecución

macOS Gatekeeper puede bloquear la app:

```
"IoT Sentry.app no se puede abrir porque es de un
desarrollador no identificado"
```

**Solución**:

1. **Preferencias del Sistema** → **Seguridad y Privacidad**
2. Click en **"Abrir de todas formas"**

O desde terminal:
```bash
xattr -cr "dist/IoT Sentry.app"
```

### Permisos Requeridos

La app pedirá permisos para:
- ✅ **Acceso a red** (para escaneo)
- ✅ **Notificaciones** (para alertas)

**Primera vez**: Ejecutar con sudo
```bash
sudo open "dist/IoT Sentry.app"
```

---

## 🐛 Troubleshooting

### Problema 1: "No module named 'XXX'"

**Causa**: Dependencia no incluida

**Solución**: Editar `setup.py`
```python
OPTIONS = {
    'packages': [
        'rumps',
        'PyQt6',
        'tu_modulo_faltante',  # ← Añadir aquí
    ],
}
```

### Problema 2: "App crashes al iniciar"

**Debug**: Ejecutar desde terminal
```bash
"dist/IoT Sentry.app/Contents/MacOS/IoT Sentry"
```

Ver logs de error y corregir.

### Problema 3: "Iconos no se ven"

**Causa**: Ruta incorrecta de assets

**Solución**: Verificar `DATA_FILES` en `setup.py`
```python
DATA_FILES = [
    ('assets', ['assets/shield.png', ...]),
]
```

### Problema 4: "La app es muy grande"

**Normal**: ~130 MB es típico para app con Python + PyQt6

**Reducir tamaño**:
- Usar `--optimize=2` en py2app
- Excluir módulos no usados
- Comprimir en DMG

---

## 🎨 Personalización

### Cambiar Icono de la App

1. Crear icono .icns:
```bash
# Convertir PNG a ICNS
# Requiere iconutil (incluido en macOS)
mkdir shield.iconset
sips -z 16 16     assets/shield_128.png --out shield.iconset/icon_16x16.png
sips -z 32 32     assets/shield_128.png --out shield.iconset/icon_16x16@2x.png
sips -z 32 32     assets/shield_128.png --out shield.iconset/icon_32x32.png
sips -z 64 64     assets/shield_128.png --out shield.iconset/icon_32x32@2x.png
sips -z 128 128   assets/shield_128.png --out shield.iconset/icon_128x128.png
sips -z 256 256   assets/shield_128.png --out shield.iconset/icon_128x128@2x.png
iconutil -c icns shield.iconset
```

2. Usar en setup.py:
```python
OPTIONS = {
    'iconfile': 'shield.icns',  # ← Archivo .icns
}
```

### Cambiar Nombre en Menu Bar

Editar `setup.py`:
```python
OPTIONS = {
    'plist': {
        'CFBundleName': 'Mi App',  # Nombre corto
        'CFBundleDisplayName': 'Mi Aplicación',  # Nombre completo
    },
}
```

---

## 📤 Distribución

### Para ti mismo:
```bash
# Copiar a /Applications
cp -r "dist/IoT Sentry.app" /Applications/
```

### Para otros usuarios:

#### Opción 1: DMG
```bash
# Crear DMG
hdiutil create -volname "IoT Sentry" \
               -srcfolder "dist/IoT Sentry.app" \
               -ov -format UDZO \
               "IoT Sentry-v1.0.0.dmg"

# Compartir el .dmg
```

#### Opción 2: ZIP
```bash
# Comprimir
cd dist
zip -r "IoT Sentry-v1.0.0.zip" "IoT Sentry.app"
```

### ⚠️ Para distribución pública:

**Requiere**:
- Firma de código (Apple Developer Account $99/año)
- Notarización de Apple
- Distribución fuera del App Store

**Sin firma**: Los usuarios verán advertencias de seguridad.

---

## 🔄 Actualizar la App

### Proceso:

1. **Modificar código**
2. **Incrementar versión** en `setup.py`:
   ```python
   'CFBundleVersion': '1.0.1',
   ```
3. **Re-empaquetar**:
   ```bash
   ./build_macos.sh
   ```
4. **Instalar nueva versión**

---

## 📊 Comparación

| Método | Ventajas | Desventajas |
|--------|----------|-------------|
| **Script (./RUN.sh)** | Fácil desarrollo | Requiere terminal |
| **App (.app)** | Nativa, profesional | Setup inicial |
| **DMG** | Fácil distribución | Tamaño grande |

---

## 🎯 Checklist Final

Antes de distribuir:

- [ ] App se ejecuta sin errores
- [ ] Iconos se ven correctamente
- [ ] Menu bar funciona
- [ ] Dashboard se abre
- [ ] Permisos funcionan
- [ ] Info.plist correcto
- [ ] Versión actualizada
- [ ] README incluido

---

## 📝 Comandos Útiles

```bash
# Build
./build_macos.sh

# Limpiar builds anteriores
rm -rf build dist

# Ver tamaño
du -sh "dist/IoT Sentry.app"

# Instalar
cp -r "dist/IoT Sentry.app" /Applications/

# Crear DMG
hdiutil create -volname "IoT Sentry" \
               -srcfolder "dist/IoT Sentry.app" \
               -ov -format UDZO \
               "IoT Sentry-v1.0.0.dmg"

# Debug
"dist/IoT Sentry.app/Contents/MacOS/IoT Sentry"

# Remover atributos de cuarentena
xattr -cr "dist/IoT Sentry.app"
```

---

**¡Tu app está lista para distribución!** 📦✨
