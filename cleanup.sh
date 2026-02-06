#!/bin/bash
# Script de limpieza del proyecto IoT Sentry

clear
echo "🧹 Limpieza del Proyecto IoT Sentry"
echo "===================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "menubar_main.py" ]; then
    echo "❌ Error: Ejecuta desde el directorio raíz del proyecto"
    exit 1
fi

echo "📋 Archivos que se borrarán:"
echo ""
echo "Docker/Web (obsoleto):"
echo "  • docker-compose.yml"
echo "  • Dockerfile"
echo "  • dashboard/"
echo ""
echo "READMEs obsoletos:"
echo "  • README_NEW.md"
echo "  • QUICKSTART.md"
echo "  • STATUS.md"
echo "  • PROGRESS.md"
echo ""
echo "Docs duplicadas:"
echo "  • MENUBAR_README.md"
echo "  • QUICK_START_MENUBAR.md"
echo "  • INSTALACION_COMPLETA.md"
echo "  • CAMBIOS_MENU.md"
echo "  • CAMBIOS_FINALES.md"
echo "  • RESUMEN_FINAL.md"
echo ""
echo "Scripts redundantes:"
echo "  • run_menubar.sh"
echo "  • START.sh"
echo ""
echo "Tests obsoletos:"
echo "  • test_app.py"
echo "  • test_enhanced_identifier.py"
echo "  • test_performance.py"
echo ""
echo "Otros:"
echo "  • network-monitor-icons.jsx"
echo "  • scripts/"
echo "  • shared/"
echo "  • desktop/"
echo ""

# Preguntar confirmación
read -p "¿Continuar con la limpieza? (s/N): " confirm

if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
    echo ""
    echo "❌ Limpieza cancelada"
    exit 0
fi

echo ""
echo "🗑️  Eliminando archivos..."
echo ""

# Contador
count=0

# Docker/Web (obsoleto)
if [ -f "docker-compose.yml" ]; then
    rm -f docker-compose.yml
    echo "  ✅ docker-compose.yml"
    ((count++))
fi

if [ -f "Dockerfile" ]; then
    rm -f Dockerfile
    echo "  ✅ Dockerfile"
    ((count++))
fi

if [ -d "dashboard" ]; then
    rm -rf dashboard/
    echo "  ✅ dashboard/"
    ((count++))
fi

# READMEs obsoletos
for file in README_NEW.md QUICKSTART.md STATUS.md PROGRESS.md; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  ✅ $file"
        ((count++))
    fi
done

# Docs duplicadas
for file in MENUBAR_README.md QUICK_START_MENUBAR.md INSTALACION_COMPLETA.md CAMBIOS_MENU.md CAMBIOS_FINALES.md RESUMEN_FINAL.md; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  ✅ $file"
        ((count++))
    fi
done

# Scripts redundantes
for file in run_menubar.sh START.sh; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  ✅ $file"
        ((count++))
    fi
done

# Tests obsoletos
for file in test_app.py test_enhanced_identifier.py test_performance.py; do
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "  ✅ $file"
        ((count++))
    fi
done

# Otros
if [ -f "network-monitor-icons.jsx" ]; then
    rm -f network-monitor-icons.jsx
    echo "  ✅ network-monitor-icons.jsx"
    ((count++))
fi

if [ -d "scripts" ]; then
    rm -rf scripts/
    echo "  ✅ scripts/"
    ((count++))
fi

if [ -d "shared" ]; then
    rm -rf shared/
    echo "  ✅ shared/"
    ((count++))
fi

if [ -d "desktop" ]; then
    rm -rf desktop/
    echo "  ✅ desktop/"
    ((count++))
fi

echo ""
echo "===================================="
echo ""
echo "✅ LIMPIEZA COMPLETADA"
echo ""
echo "📊 Estadísticas:"
echo "   • Archivos/directorios eliminados: $count"
echo ""
echo "📁 Estructura actual:"
tree -L 1 -I 'venv|__pycache__|*.pyc|build|dist|.git' 2>/dev/null || ls -1
echo ""
echo "💡 Siguiente paso:"
echo "   ./RUN.sh"
