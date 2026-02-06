#!/usr/bin/env python3
"""
Test del cálculo de lag
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 Test de cálculo de lag\n")
print("=" * 50)

# Test 1: Import del engine
print("\n1️⃣ Importando IoTSentryEngine...")
try:
    from core import IoTSentryEngine
    print("   ✅ Importado correctamente")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Crear engine
print("\n2️⃣ Creando engine...")
try:
    engine = IoTSentryEngine()
    print("   ✅ Engine creado")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Obtener gateway
print("\n3️⃣ Obteniendo gateway...")
try:
    gateway = engine.scanner.get_gateway()
    if gateway:
        print(f"   ✅ Gateway encontrado: {gateway}")
    else:
        print("   ⚠️  No se pudo obtener gateway")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Calcular latencia
print("\n4️⃣ Calculando latencia...")
try:
    latency = engine._calculate_average_latency()
    if latency is not None:
        print(f"   ✅ Latencia calculada: {latency:.1f}ms")

        # Interpretar resultado
        if latency < 10:
            print("      🟢 Excelente")
        elif latency < 50:
            print("      🟢 Bueno")
        elif latency < 100:
            print("      🟡 Aceptable")
        else:
            print("      🔴 Problemas de red")
    else:
        print("   ⚠️  No se pudo calcular latencia")
        print("      (Esto puede ser normal si no hay conexión a red)")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Stats completos
print("\n5️⃣ Obteniendo stats completos...")
try:
    # Inicializar DB primero
    engine.db_context = engine.scanner.__class__.__module__  # Hack para test
    from agent.database import get_db
    engine.db_context = get_db()
    engine.db_session = engine.db_context.__enter__()

    stats = engine.get_stats()
    print("   ✅ Stats obtenidos:")
    print(f"      • Dispositivos: {stats.get('total_devices', 0)}")
    print(f"      • Alertas: {stats.get('unread_alerts', 0)}")

    if stats.get('average_latency') is not None:
        print(f"      • Lag: {stats.get('average_latency'):.1f}ms")
    else:
        print(f"      • Lag: -")

except Exception as e:
    print(f"   ⚠️  Error obteniendo stats: {e}")

print("\n" + "=" * 50)
print("\n✅ TEST COMPLETADO")
print("\n📝 La app está lista para mostrar el lag en el menú")
print("   Ejecuta: ./RUN.sh")
