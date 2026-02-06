# Monitor de Rendimiento - IoT Sentry

Nueva funcionalidad implementada para detectar LAG y analizar tráfico de red.

## 📊 Tab de Rendimiento

### Acceso:
En la aplicación, ir al tab **"📊 Rendimiento"**

---

## 🔍 Funcionalidad 1: Detector de LAG

### ¿Qué hace?

Mide continuamente la latencia de tu red y diagnostica problemas de rendimiento.

### Métricas que monitorea:

```
🟢 EXCELENTE - Red funcionando óptimamente

📊 Latencias:
  • Router: 3ms
  • Internet: 18ms
  • Jitter: 5ms

✅ Red funcionando óptimamente
```

### Estados posibles:

| Estado | Emoji | Descripción |
|--------|-------|-------------|
| **Excelente** | 🟢 | < 10ms router, < 50ms internet, < 10ms jitter |
| **Buena** | 🟢 | < 50ms router, < 100ms internet, < 20ms jitter |
| **Aceptable** | 🟡 | < 100ms router, < 150ms internet, < 30ms jitter |
| **Mala** | 🟠 | < 200ms router, < 300ms internet, < 50ms jitter |
| **Crítica** | 🔴 | > 200ms router o sin conectividad |

### ¿Qué mide?

#### 1. **Latencia al Router** (ping a 192.168.1.1)
```
✅ < 10ms   - Excelente
⚠️ 10-50ms  - Normal
⚠️ 50-100ms - Alto (posible congestión local)
❌ > 100ms  - Crítico (problema en red local)
```

**Causas comunes de latencia alta al router:**
- Demasiados dispositivos conectados
- Señal WiFi débil
- Interferencia de redes vecinas
- Router sobrecargado

#### 2. **Latencia a Internet** (ping a 8.8.8.8, 1.1.1.1)
```
✅ < 30ms   - Excelente
⚠️ 30-80ms  - Normal
⚠️ 80-150ms - Alto
❌ > 150ms  - Crítico (problema con ISP)
```

**Causas comunes:**
- Distancia al servidor
- Congestión del ISP
- Plan de internet lento
- Problemas en la red del proveedor

#### 3. **Jitter** (variación de latencia)
```
✅ < 10ms   - Excelente para todo
⚠️ 10-20ms  - OK para navegación, no ideal para gaming
⚠️ 20-30ms  - Malo para videollamadas
❌ > 30ms   - Crítico para aplicaciones en tiempo real
```

**¿Por qué importa el jitter?**
- **Videollamadas**: Jitter alto = cortes y pixelación
- **Gaming**: Jitter alto = movimientos erráticos
- **VoIP**: Jitter alto = audio entrecortado

### Diagnóstico Automático

El sistema analiza las métricas y proporciona diagnóstico:

```
⚠️  Latencia alta al router: 85ms

💡 Recomendaciones:
   → Posible congestión en red local
   → Verificar dispositivos consumiendo mucho ancho de banda
```

### Ejemplos de Diagnósticos:

#### Caso 1: Red sobrecargada
```
🟠 MALA

📊 Latencias:
  • Router: 125ms
  • Internet: 145ms
  • Jitter: 45ms

⚠️ Latencia alta al router: 125ms
⚠️ Jitter alto: 45ms

💡 Recomendaciones:
   → Posible congestión en red local
   → Verificar dispositivos consumiendo mucho ancho de banda
   → Red inestable - malo para videollamadas y gaming
   → Reducir número de dispositivos activos
```

#### Caso 2: Problema con ISP
```
🟡 ACEPTABLE

📊 Latencias:
  • Router: 5ms
  • Internet: 185ms
  • Jitter: 12ms

⚠️ Latencia alta a internet: 185ms

💡 Recomendaciones:
   → Problema puede estar en el ISP
   → Contactar proveedor de internet
```

---

## 🧛 Funcionalidad 2: Detector de Vampiros de Ancho de Banda

### ¿Qué hace?

Identifica qué dispositivos están consumiendo más ancho de banda y te avisa si alguno está "chupando" demasiado.

### Períodos de análisis:

- **Última hora**: Para problemas actuales
- **Últimas 6 horas**: Patrones recientes
- **Últimas 24 horas**: Comportamiento diario

### Ejemplo de salida:

```
⚠️  2 vampiro(s) detectado(s):

🔴 Samsung-TV
   Consumo: 65% del total (45.2 Mbps promedio)
   Total: 1,250 MB en 6h

🟠 Roomba-785
   Consumo: 22% del total (15.1 Mbps promedio)
   Total: 405 MB en 6h

💡 Recomendaciones:
• Pausar streaming de video durante videollamadas importantes
• Programar backups/actualizaciones para horarios nocturnos
• Considerar limitar ancho de banda de dispositivos específicos en el router
```

### Umbrales de Vampiros:

| Consumo | Severidad | Emoji | Descripción |
|---------|-----------|-------|-------------|
| > 50% | **Crítico** | 🔴 | Monopolizando la red |
| 30-50% | **Alto** | 🟠 | Consumo muy elevado |
| 15-30% | **Medio** | 🟡 | Consumo notable |
| < 15% | Normal | ✅ | No se reporta |

### Causas comunes de vampiros:

#### Smart TV (típicamente el #1):
- Streaming 4K: 25 Mbps
- Streaming HD: 5-8 Mbps
- Actualizaciones automáticas
- **Solución**: Bajar calidad a 1080p cuando otros usen la red

#### Aspiradoras Robot:
- Subida de mapas en tiempo real
- Transmisión de video
- **Solución**: Programar limpieza cuando no necesites banda ancha

#### Cámaras IP:
- Streaming continuo a la nube
- Grabación en alta resolución
- **Solución**: Configurar grabación local o reducir calidad

#### Backups automáticos:
- Computadoras haciendo backup a la nube
- NAS sincronizando archivos
- **Solución**: Programar para 2-6 AM

---

## 📈 Funcionalidad 3: Gráficos de Tráfico Temporal

### ¿Qué muestra?

Un gráfico en tiempo real que visualiza el consumo de ancho de banda hora por hora en las últimas 24 horas.

### Ejemplo visual:

```
Mbps
50 │           ╭─╮
40 │       ╭───╯ ╰╮
30 │   ╭───╯      ╰─╮
20 │╭──╯            ╰───╮
10 │                     ╰──
 0 └─────────────────────────
   0h   6h   12h   18h   24h
```

### Opciones:

**Mostrar:**
- **Todos los dispositivos**: Tráfico total de la red
- **Por dispositivo individual**: Seleccionar en dropdown

### ¿Para qué sirve?

#### 1. Identificar patrones de uso:
```
Pico a las 8 AM → Reunión Zoom
Pico a las 3 PM → Niños viendo YouTube
Pico a las 11 PM → Backup automático
```

#### 2. Detectar actividad sospechosa:
```
Cámara-Garage tiene picos de tráfico a las 3 AM
→ ¿Alguien está accediendo?
→ ¿Está siendo hackeada?
```

#### 3. Optimizar horarios:
```
Ver cuándo la red está libre para programar:
- Descargas grandes
- Backups
- Actualizaciones del sistema
```

#### 4. Validar límites del plan:
```
Si el gráfico muestra constantemente 90-100 Mbps
y tu plan es de 100 Mbps → Necesitas upgrade
```

---

## 🛠️ Cómo usar el Monitor de Rendimiento

### Paso 1: Abrir tab de Rendimiento

```
IoT Sentry → Tab "📊 Rendimiento"
```

### Paso 2: Diagnóstico inicial

Click en **"🔄 Analizar Ahora"** para hacer medición inmediata.

La aplicación también analiza automáticamente cada 10 segundos.

### Paso 3: Interpretar resultados

#### Si ves 🟢 EXCELENTE:
✅ Tu red está perfecta, no hay acciones necesarias

#### Si ves 🟡 ACEPTABLE:
⚠️ La red funciona pero hay margen de mejora
- Revisa sección de vampiros
- Considera reducir dispositivos activos

#### Si ves 🟠 MALA o 🔴 CRÍTICA:
❌ Hay problemas serios
- Sigue las recomendaciones específicas
- Verifica vampiros de ancho de banda
- Considera contactar tu ISP

### Paso 4: Revisar vampiros

Selecciona período de análisis y revisa la lista.

**Si hay vampiros:**
1. Identifica el dispositivo problemático
2. Sigue las recomendaciones
3. Pausa/limita ese dispositivo temporalmente

### Paso 5: Analizar gráfico

Observa patrones en las últimas 24h:

- **Picos constantes**: Normal si corresponde a tu uso
- **Picos inesperados**: Investigar qué dispositivo causa esto
- **Actividad nocturna alta**: Probablemente backups automáticos

---

## 💡 Casos de Uso Reales

### Caso 1: "Mi Zoom se corta todo el tiempo"

**Problema**: Videollamadas con lag y cortes

**Diagnóstico en IoT Sentry**:
```
🟠 MALA
Jitter: 42ms
Vampiro detectado: Smart-TV (streaming 4K)
```

**Solución**:
1. Pausar Netflix en la TV durante la llamada
2. O configurar QoS en el router para priorizar Zoom

---

### Caso 2: "El gaming tiene lag horrible"

**Problema**: Juegos online injugables

**Diagnóstico en IoT Sentry**:
```
🟡 ACEPTABLE
Internet: 125ms
Vampiros: Roomba-785 (35%), iCloud-Backup (28%)
```

**Solución**:
1. Programar Roomba para otro horario
2. Pausar backups de iCloud durante gaming
3. Resultado: Latencia baja a 25ms ✅

---

### Caso 3: "La red está lenta pero no sé por qué"

**Problema**: Internet generalmente lento

**Diagnóstico en IoT Sentry**:
```
🟢 EXCELENTE (latencia OK)
Pero vampiro: NAS-Synology (82% del ancho de banda)
Gráfico: Picos constantes las últimas 12 horas
```

**Solución**:
1. NAS está sincronizando archivos grandes
2. Pausar sincronización o programarla para la noche
3. Internet vuelve a velocidad normal ✅

---

### Caso 4: "¿Debo upgradear mi plan de internet?"

**Diagnóstico en IoT Sentry**:
```
Gráfico muestra consumo constante de 95-100 Mbps
Plan contratado: 100 Mbps
Vampiros: Múltiples dispositivos streaming simultáneamente
```

**Conclusión**:
Sí, necesitas upgrade a plan de 200+ Mbps

---

## 🔧 Configuración Avanzada

### Ajustar intervalo de medición

Por defecto mide cada 10 segundos. Para cambiarlo:

```python
# En performance_tab.py
self.update_timer.start(5000)  # 5 segundos (más frecuente)
# o
self.update_timer.start(30000)  # 30 segundos (menos frecuente)
```

### Ajustar umbral de vampiros

Por defecto: 15% del tráfico total. Para cambiarlo:

```python
# En bandwidth_analyzer.py
vampires = self.detect_bandwidth_hogs(hours, threshold_percentage=10.0)  # Más sensible
```

---

## 📊 Comparación: Antes vs Después

### ANTES (sin IoT Sentry):
```
Usuario: "Mi internet está lento"
→ No sabe por qué
→ No sabe qué dispositivo causa el problema
→ Llama al ISP (que no puede ayudar)
→ Frustrción y pérdida de tiempo
```

### DESPUÉS (con IoT Sentry):
```
Usuario: "Mi internet está lento"
→ Abre IoT Sentry → Tab Rendimiento
→ Ve: Smart-TV consumiendo 78% del ancho de banda
→ Pausa Netflix
→ Internet funciona perfectamente ✅
Tiempo total: 30 segundos
```

---

## ❓ FAQ

**P: ¿Por qué mi latencia al router es alta pero a internet es normal?**
R: Problema en tu red local (WiFi débil, interferencia, muchos dispositivos). No es culpa del ISP.

**P: ¿Qué es mejor: baja latencia o alto ancho de banda?**
R: Depende del uso:
- Gaming/videollamadas: Latencia baja es CRÍTICA
- Descargas/streaming: Ancho de banda alto es más importante

**P: ¿El jitter alto siempre es malo?**
R: Solo si haces videollamadas o gaming. Para navegación web no importa mucho.

**P: ¿Por qué mi cámara es un "vampiro"?**
R: Probablemente está subiendo video continuamente a la nube. Configúrala para grabación local.

**P: ¿Cómo sé si necesito upgradear mi plan de internet?**
R: Si el gráfico muestra constantemente 90-100% de tu capacidad contratada durante el día.

---

## 🎯 Resumen

El Monitor de Rendimiento te da:

✅ **Visibilidad**: Saber qué está pasando en tu red
✅ **Diagnóstico**: Identificar problemas automáticamente
✅ **Acción**: Recomendaciones específicas para resolver
✅ **Prevención**: Detectar problemas antes de que te afecten

**Resultado**: Red más rápida, menos LAG, mejor experiencia online.

---

**Última actualización**: 2026-02-06
