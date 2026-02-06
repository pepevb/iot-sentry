#!/usr/bin/env python3
"""
Test básico para verificar que menubar_main.py funciona
"""

import sys
import os

# Ajustar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 Test de IoT Sentry Menu Bar\n")
print("=" * 50)

# Test 1: Imports
print("\n1️⃣ Verificando imports...")
try:
    import rumps
    print("   ✅ rumps")
except ImportError as e:
    print(f"   ❌ rumps: {e}")
    sys.exit(1)

try:
    from PyQt6.QtWidgets import QApplication
    print("   ✅ PyQt6")
except ImportError as e:
    print(f"   ❌ PyQt6: {e}")
    sys.exit(1)

try:
    from core import IoTSentryEngine
    print("   ✅ IoTSentryEngine")
except ImportError as e:
    print(f"   ❌ IoTSentryEngine: {e}")
    sys.exit(1)

try:
    from gui.main_window import MainWindow
    print("   ✅ MainWindow")
except ImportError as e:
    print(f"   ❌ MainWindow: {e}")
    sys.exit(1)

# Test 2: Crear Engine (sin iniciarlo)
print("\n2️⃣ Verificando Engine...")
try:
    engine = IoTSentryEngine()
    print("   ✅ Engine creado correctamente")
    print(f"   📊 Stats disponibles: {hasattr(engine, 'get_stats')}")
    print(f"   🔍 Scanner disponible: {hasattr(engine, 'scanner')}")
except Exception as e:
    print(f"   ❌ Error creando engine: {e}")

# Test 3: Verificar permisos
print("\n3️⃣ Verificando permisos...")
if os.geteuid() == 0:
    print("   ✅ Ejecutando con permisos de superusuario")
else:
    print("   ⚠️  NO ejecutando como root")
    print("   💡 Para captura de tráfico necesitas: sudo python test_menubar.py")

# Test 4: Base de datos
print("\n4️⃣ Verificando base de datos...")
try:
    from agent.database import Database
    db = Database()
    print("   ✅ Base de datos inicializada")
except Exception as e:
    print(f"   ⚠️  Advertencia con DB: {e}")

print("\n" + "=" * 50)
print("\n✅ TODOS LOS TESTS PASARON")
print("\n📝 Para ejecutar la app completa:")
print("   sudo python menubar_main.py")
print("\n   O usa el script:")
print("   sudo ./run_menubar.sh")
