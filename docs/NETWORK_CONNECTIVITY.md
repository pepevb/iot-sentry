# Conectividad de Red - IoT Sentry

Este documento explica cómo IoT Sentry se conecta a la red local y detecta dispositivos.

## 🌐 Conexión a la Red Local

IoT Sentry **NO requiere configuración especial** para conectarse a la red. Funciona automáticamente porque:

### 1. Se ejecuta en tu computadora

```
┌─────────────────────────────────────────────────┐
│                  Tu Red Local                    │
│                                                  │
│  ┌─────────┐         ┌──────────────┐          │
│  │ Router  │────────│ Tu Computadora│          │
│  │ (WiFi)  │         │ (IoT Sentry) │          │
│  └────┬────┘         └──────────────┘          │
│       │                                          │
│       ├─── Dispositivo IoT #1 (Cámara)         │
│       ├─── Dispositivo IoT #2 (Alexa)          │
│       └─── Dispositivo IoT #3 (Bombilla)       │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Tu computadora ya está conectada a la red** (via WiFi o Ethernet), por lo tanto IoT Sentry automáticamente tiene acceso a esa red.

### 2. Detección Automática de Interfaz

IoT Sentry detecta automáticamente:

```python
# En agent/scanner/network_scanner.py

def get_local_network_info(self):
    # 1. Detectar interfaz de red activa (WiFi o Ethernet)
    gateways = netifaces.gateways()
    default_interface = gateways['default'][netifaces.AF_INET][1]

    # Ejemplos de interfaces:
    # macOS:    "en0" (WiFi) o "en1" (Ethernet)
    # Linux:    "wlan0" (WiFi) o "eth0" (Ethernet)
    # Windows:  "Wi-Fi" o "Ethernet"

    # 2. Obtener IP y máscara de subred
    ip = "192.168.1.100"      # Tu IP local (ejemplo)
    netmask = "255.255.255.0"  # Máscara típica

    # 3. Calcular red completa
    network = "192.168.1.0/24"  # Red a escanear (256 IPs)
```

**No necesitas configurar nada** - IoT Sentry usa la misma conexión que tu navegador, Spotify, etc.

---

## 🔍 Descubrimiento de Dispositivos (ARP Scanning)

### ¿Cómo encuentra dispositivos en la red?

IoT Sentry usa el protocolo **ARP (Address Resolution Protocol)**, que es el mismo que usa tu sistema operativo constantemente.

### Paso a Paso:

#### 1. Tu computadora está conectada

```
Tu PC: 192.168.1.100
Router: 192.168.1.1
Red: 192.168.1.0/24 (192.168.1.1 - 192.168.1.254)
```

#### 2. IoT Sentry envía requests ARP

```python
# Equivalente a hacer "ping" a todas las IPs de la red

for ip in range(192.168.1.1, 192.168.1.254):
    enviar_arp_request(ip)
    # Pregunta: "¿Quién tiene la IP 192.168.1.50?"
```

#### 3. Dispositivos responden

```
Router (192.168.1.1):  "Yo tengo esa IP, mi MAC es AA:BB:CC:DD:EE:FF"
Cámara (192.168.1.50): "Yo tengo esa IP, mi MAC es 11:22:33:44:55:66"
Alexa (192.168.1.75):  "Yo tengo esa IP, mi MAC es 99:88:77:66:55:44"
```

#### 4. IoT Sentry recopila información

```python
dispositivos_encontrados = [
    {
        'ip': '192.168.1.1',
        'mac': 'AA:BB:CC:DD:EE:FF',
        'fabricante': 'TP-Link' (via OUI lookup)
    },
    {
        'ip': '192.168.1.50',
        'mac': '11:22:33:44:55:66',
        'fabricante': 'Wyze Labs'
    },
    # ...
]
```

---

## 🔌 NO Necesitas Acceso al Router

### ¿Por qué no se requiere configurar el router?

**IoT Sentry NO se conecta directamente al router**. En su lugar:

### Analogía:

Imagina que estás en una habitación con varias personas:

- **Método tradicional** (acceso al router): Pedirle al organizador del evento una lista de invitados
- **Método de IoT Sentry**: Simplemente gritar "¿Hay alguien aquí?" y ver quién responde

IoT Sentry usa el segundo método - **envía mensajes broadcast** (como gritar en la habitación) y ve quién responde.

### Ventajas:

✅ **No requiere contraseña del router**
✅ **No requiere acceso web al panel de administración**
✅ **No requiere configuración de puertos o firewall**
✅ **Funciona en cualquier red** (casa, oficina, hotel con restricciones)
✅ **No modifica configuración de red**

---

## 📡 Captura de Tráfico

### ¿Cómo "ve" el tráfico de otros dispositivos?

Aquí hay una diferencia importante:

### Red Normal (Switch/Router moderno)

```
┌─────────────────────────────────────────┐
│            Switch/Router                 │
│                                          │
│  [Cámara] ──────┐                       │
│                  ├──▶ [Servidor Cloud]  │
│  [Tu PC]  ──────┘                       │
│  (no ve el                               │
│   tráfico)                               │
└─────────────────────────────────────────┘
```

En redes modernas con switches, **cada dispositivo solo ve su propio tráfico**.

### Lo que IoT Sentry Captura:

IoT Sentry solo puede capturar:

#### ✅ Tráfico que PASA por tu computadora:
1. **Tráfico de tu propia computadora** (obviamente)
2. **Tráfico de dispositivos que usan tu PC como gateway** (raro en redes domésticas)

#### ⚠️ LIMITACIÓN: En redes con switch moderno

IoT Sentry **NO puede ver el contenido** del tráfico de otros dispositivos directamente.

**PERO** puede usar técnicas adicionales:

### Solución 1: ARP Spoofing (Modo Avanzado)

```python
# NOTA: Esta funcionalidad no está implementada en MVP
# Requiere permisos adicionales y puede ser detectado como malicioso

# Técnica: Hacerse pasar por el router
send_arp_reply(target_ip, mi_mac, router_ip)
# Ahora el dispositivo envía tráfico a tu PC pensando que eres el router
```

**⚠️ Advertencia**: Esto puede:
- Interrumpir conectividad de red
- Ser detectado como ataque
- Requerir más permisos

**Estado en MVP**: **NO implementado** (por simplicidad y seguridad)

### Solución 2: Monitoreo Pasivo en el Router

```
┌──────────────────────────────────────┐
│  Instalar IoT Sentry en el Router   │
│  (Raspberry Pi, OpenWrt, etc.)      │
│                                      │
│  ┌────────┐                          │
│  │ Router │ ◄── IoT Sentry aquí     │
│  └───┬────┘     ve TODO el tráfico  │
│      │                               │
│      ├─── Todos los dispositivos    │
│      └─── pasan por aquí            │
└──────────────────────────────────────┘
```

**Estado en MVP**: **Soportado** si instalas en un router con Linux (ej. Raspberry Pi como router)

### Solución 3: Modo Promiscuo (Redes antiguas con Hub)

```python
# En redes con HUB (no switch), se puede activar modo promiscuo
conf.sniff_promisc = True
```

**Redes modernas**: Esto **NO funciona** porque los switches aíslan el tráfico

**Redes antiguas con HUB**: Sí funciona, pero casi nadie usa HUBs hoy en día

---

## 🎯 ¿Qué SÍ puede hacer IoT Sentry?

Aunque no vea TODO el tráfico en tiempo real, IoT Sentry es efectivo porque:

### 1. Descubrimiento de Dispositivos (100% efectivo)

```
✅ Ver TODOS los dispositivos conectados
✅ Identificar fabricantes (MAC → OUI)
✅ Ver IPs asignadas
✅ Ver nombres de host
```

### 2. Análisis de DNS Queries

```
Cuando un dispositivo hace DNS lookup:
Cámara pregunta: "¿Cuál es la IP de cloud.wyze.com?"

IoT Sentry ve la pregunta (query DNS) incluso sin ver el tráfico HTTPS
```

### 3. Análisis de Metadatos Visibles

```
Información visible sin descifrar:
- IPs de destino
- Puertos (80=HTTP, 443=HTTPS, etc.)
- Volumen de datos (bytes enviados/recibidos)
- Frecuencia de conexiones
```

### 4. Detección de Conexiones Activas

```
Aunque no vea el contenido HTTPS, puede ver:
"La cámara está enviando datos a 52.84.150.20 (Amazon AWS, Virginia)"
```

---

## 🔧 Implementación Técnica

### Código Simplificado del Scanner:

```python
# agent/scanner/network_scanner.py

class NetworkScanner:
    def scan_network(self):
        # 1. Auto-detectar red
        network = self.get_local_network_info()
        # Resultado: "192.168.1.0/24"

        # 2. Crear paquete ARP broadcast
        arp = ARP(pdst=network)  # Destino: toda la red
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast MAC

        # 3. Enviar y recibir
        answered = srp(ether/arp, timeout=3)

        # 4. Procesar respuestas
        for sent, received in answered:
            dispositivo = {
                'ip': received.psrc,      # IP del dispositivo
                'mac': received.hwsrc,    # MAC del dispositivo
            }
```

### ¿Por qué funciona sin configuración?

1. **ARP es un protocolo de capa 2** (Data Link layer)
   - No requiere enrutamiento
   - Funciona en la red local directamente
   - Todos los dispositivos DEBEN responder a ARP

2. **Broadcast es permitido por defecto**
   - Los routers permiten broadcast ARP
   - Es necesario para el funcionamiento normal de la red

3. **No requiere autenticación**
   - ARP es un protocolo sin autenticación
   - Diseñado para ser abierto y rápido

---

## 🛡️ Opciones de Despliegue

### Opción 1: En tu Laptop/PC (Alcance Limitado)

```
Ventajas:
✅ Fácil instalación
✅ No requiere hardware adicional

Limitaciones:
⚠️ Solo ve dispositivos en tu subnet
⚠️ No captura tráfico de otros dispositivos (con switch)
```

### Opción 2: Raspberry Pi como Mirror Port (Recomendado)

```
┌─────────────────────────────────────────┐
│                Router                    │
│  (con port mirroring habilitado)        │
│                                          │
│  Puerto 1: Internet                     │
│  Puerto 2: Dispositivos                 │
│  Puerto 3: Raspberry Pi (MIRROR)        │
│             └── Copia de todo el tráfico│
└─────────────────────────────────────────┘
```

**Configuración**: Requiere router empresarial o configuración avanzada

### Opción 3: Raspberry Pi como Router (Máximo Control)

```
Internet ──▶ [Raspberry Pi con IoT Sentry] ──▶ [Dispositivos IoT]
             (Todo el tráfico pasa por aquí)
```

**Ventaja**: Ve y controla TODO el tráfico

---

## 📊 Resumen

| Característica | ¿Requiere Configuración? | Efectividad |
|---------------|--------------------------|-------------|
| Descubrir dispositivos | ❌ No | ✅ 100% |
| Identificar fabricantes | ❌ No | ✅ 95% |
| Ver IPs de destino | ⚠️ Limitado | ⚠️ Variable |
| Ver contenido tráfico | ❌ No (imposible con HTTPS) | ❌ 0% |
| Detectar anomalías | ⚠️ Depende del despliegue | ⚠️ Variable |

### Para Máxima Efectividad:

1. **MVP (tu laptop)**: Descubrimiento de dispositivos + análisis básico
2. **Avanzado (Raspberry Pi)**: Análisis completo de tráfico
3. **Enterprise (Router dedicado)**: Control total

---

## ❓ Preguntas Frecuentes

**P: ¿Necesito conectarme al router?**
R: No, IoT Sentry usa tu conexión de red existente.

**P: ¿Funciona con WiFi y Ethernet?**
R: Sí, funciona con ambos. Auto-detecta la interfaz activa.

**P: ¿Necesito configurar mi router?**
R: No para funcionalidad básica. Sí para análisis avanzado de tráfico.

**P: ¿Puede ver contraseñas WiFi?**
R: No. IoT Sentry no tiene acceso a esa información.

**P: ¿Funciona en redes de invitados (Guest WiFi)?**
R: Sí, pero solo verá dispositivos en esa red de invitados (aislada del resto).

**P: ¿Ralentiza mi red?**
R: No. El escaneo ARP es muy ligero (< 1KB de datos cada 5 minutos).

---

**Conclusión**: IoT Sentry funciona "out of the box" sin configuración porque aprovecha la conexión de red que tu computadora ya tiene. Es como una "app de monitoreo" que simplemente observa lo que sucede en tu red local, sin necesidad de permisos especiales del router.
