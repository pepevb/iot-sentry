#!/bin/bash
# Script para empaquetar IoT Sentry como aplicación macOS

clear
echo "📦 Empaquetando IoT Sentry para macOS"
echo "======================================"
echo ""

# Verificar directorio
if [ ! -f "menubar_main.py" ]; then
    echo "❌ Error: Ejecuta desde el directorio raíz del proyecto"
    exit 1
fi

# Activar virtualenv
echo "1️⃣ Activando virtualenv..."
source venv/bin/activate

# Instalar py2app si no está
echo ""
echo "2️⃣ Verificando py2app..."
if ! python -c "import py2app" 2>/dev/null; then
    echo "   Instalando py2app..."
    pip install py2app
fi

# Limpiar builds anteriores
echo ""
echo "3️⃣ Limpiando builds anteriores..."
rm -rf build dist

# Construir aplicación
echo ""
echo "4️⃣ Construyendo aplicación..."
python setup.py py2app

# Verificar resultado
if [ -d "dist/IoT Sentry.app" ]; then
    echo ""
    echo "======================================"
    echo "✅ APLICACIÓN CREADA CON ÉXITO"
    echo ""
    echo "📁 Ubicación: dist/IoT Sentry.app"
    echo ""
    echo "📊 Tamaño:"
    du -sh "dist/IoT Sentry.app"
    echo ""
    echo "🚀 Para ejecutar:"
    echo "   open 'dist/IoT Sentry.app'"
    echo ""
    echo "💾 Para instalar:"
    echo "   cp -r 'dist/IoT Sentry.app' /Applications/"
    echo ""
    echo "⚠️  IMPORTANTE:"
    echo "   La app requiere permisos de administrador."
    echo "   Primera ejecución: Preferencias → Seguridad"
else
    echo ""
    echo "❌ Error durante la construcción"
    echo "   Revisa los mensajes arriba"
fi
