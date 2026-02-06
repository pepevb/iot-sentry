#!/bin/bash
# Script mejorado para ejecutar IoT Sentry Menu Bar

clear
echo "🛡️  IoT Sentry Menu Bar"
echo "============================================"
echo ""

# Ir al directorio correcto
cd "$(dirname "$0")"

# Activar virtualenv
if [ ! -d "venv" ]; then
    echo "❌ Error: virtualenv no encontrado"
    echo "   Ejecuta: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

# Verificar dependencias
echo "📦 Verificando dependencias..."
if ! python -c "import rumps" 2>/dev/null; then
    echo "⚠️  Instalando rumps..."
    pip install rumps pyobjc-framework-Cocoa
fi

echo ""
echo "✅ Todo listo!"
echo ""
echo "🚀 Iniciando IoT Sentry..."
echo ""
echo "   👀 BUSCA en tu menu bar (arriba a la derecha)"
echo "      Deberías ver: 🛡️"
echo ""
echo "   📝 Si no aparece:"
echo "      - Verifica Preferencias del Sistema"
echo "      - Seguridad y Privacidad → Privacidad"
echo "      - Asegúrate que Python tiene permisos"
echo ""
echo "   ⚠️  Para captura de tráfico, ejecuta con sudo:"
echo "      sudo ./RUN.sh"
echo ""
echo "   🛑 Para detener: Ctrl+C en esta terminal"
echo "      o usa el menú: 🛡️ → Salir"
echo ""
echo "============================================"
echo ""

# Ejecutar
python menubar_main.py
