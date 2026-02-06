# Arquitectura - IoT Sentry

Este documento describe la arquitectura técnica de IoT Sentry.

## 📐 Visión General

IoT Sentry es una aplicación desktop multiplataforma con arquitectura de 3 capas:

```
┌────────────────────────────────────────────────────────────┐
│                     Desktop Application                     │
│                    (pywebview wrapper)                      │
└──────────────────────────┬─────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
┌───────────────────┐              ┌──────────────────────┐
│   Frontend Layer  │              │   Backend Layer      │
│   (Next.js SPA)   │◄────HTTP─────┤   (Python Agent)     │
│                   │   REST/WS    │                      │
│  • Dashboard UI   │              │  • Network Scanner   │
│  • Visualization  │              │  • Packet Sniffer    │
│  • User Controls  │              │  • Flow Analyzer     │
│                   │              │  • FastAPI Server    │
└───────────────────┘              └──────────┬───────────┘
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │   Data Layer        │
                                   │   (SQLite + Files)  │
                                   │                     │
                                   │  • Devices DB       │
                                   │  • Flows DB         │
                                   │  • Alerts DB        │
                                   │  • GeoLite2 DB      │
                                   │  • OUI Database     │
                                   └─────────────────────┘
```

---

## 🏗️ Componentes Principales

### 1. Desktop Wrapper (pywebview)

**Responsabilidad**: Empaquetar la aplicación web en una ventana nativa del SO

**Tecnologías**:
- `pywebview` - Wrapper nativo para Windows/macOS/Linux
- `PyInstaller` - Empaquetado en ejecutable standalone

**Funciones**:
- Iniciar FastAPI server en localhost
- Abrir ventana nativa apuntando a `http://127.0.0.1:8000`
- Manejar lifecycle (startup/shutdown)
- System tray integration (futuro)

**Archivo principal**: `/desktop/app.py`

---

### 2. Frontend Layer (Next.js)

**Responsabilidad**: Interfaz de usuario y visualización de datos

**Tecnologías**:
- Next.js 14 (App Router)
- React 18
- Tailwind CSS + shadcn/ui
- recharts (gráficos)
- react-simple-maps (mapas geográficos)

**Estructura**:
```
/dashboard
├── /app
│   ├── page.tsx              # Dashboard principal
│   ├── /devices
│   │   ├── page.tsx          # Lista de dispositivos
│   │   └── /[id]
│   │       └── page.tsx      # Detalle de dispositivo
│   ├── /map
│   │   └── page.tsx          # Mapa mundial
│   └── /alerts
│       └── page.tsx          # Centro de alertas
├── /components
│   ├── DeviceCard.tsx
│   ├── WorldMap.tsx
│   ├── TrafficChart.tsx
│   └── AlertCard.tsx
└── /lib
    └── api.ts                # Cliente API
```

**Flujo de datos**:
1. Componente hace request a API (`/api/devices`)
2. Cliente API (`lib/api.ts`) maneja HTTP/WebSocket
3. Datos se renderizan en componentes React
4. Updates en tiempo real via WebSocket

**Build**: Se compila a archivos estáticos (`next build` → `/out`)

---

### 3. Backend Layer (Python Agent)

**Responsabilidad**: Lógica de negocio, captura de datos, análisis

#### 3.1 Network Scanner (`/agent/scanner`)

**Función**: Descubrir dispositivos en red local

**Módulos**:
- `network_scanner.py`: Escaneo ARP para detectar hosts activos
  - Usa `scapy` para enviar ARP requests
  - Detecta automáticamente interfaz de red y subnet
  - Resuelve hostnames via DNS inverso

- `device_identifier.py`: Identificación de fabricantes y tipos
  - Lookup de fabricante via OUI (primeros 3 octetos de MAC)
  - Base de datos IEEE OUI (`shared/databases/oui.txt`)
  - Heurísticas para tipo de dispositivo (camera, speaker, etc.)

**Flujo**:
```
1. Detectar interfaz activa (netifaces)
2. Calcular subnet en formato CIDR
3. Enviar ARP broadcast a toda la subnet
4. Recibir respuestas con MAC + IP
5. Resolver hostname (DNS)
6. Identificar fabricante (OUI lookup)
7. Clasificar tipo de dispositivo (heurísticas)
8. Guardar en DB (tabla devices)
```

#### 3.2 Packet Sniffer (`/agent/sniffer`)

**Función**: Capturar tráfico de red de dispositivos IoT

**Módulos**:
- `packet_capture.py`: Sniffing pasivo de paquetes
  - Captura solo headers (IP, puertos, protocolo)
  - No captura payload (privacidad)
  - Filtro BPF para optimizar
  - Requiere permisos CAP_NET_RAW

- `flow_tracker.py`: Agregación de paquetes en flujos
  - Agrupa paquetes por 5-tupla (src IP, dst IP, src port, dst port, protocol)
  - Calcula bytes/packets por flujo
  - Timeout para cerrar flujos inactivos

**Flujo**:
```
1. Iniciar sniffing en interfaz de red
2. Filtrar solo IPs de dispositivos conocidos
3. Extraer: IP destino, puerto, protocolo
4. Agregar a flujo existente o crear nuevo
5. Actualizar contadores (bytes, packets)
6. Guardar flujo en DB cada N segundos
```

**Consideraciones**:
- Solo captura outbound traffic (desde dispositivos IoT)
- No descifra HTTPS/TLS (imposible y poco ético)
- Solo metadatos, nunca contenido

#### 3.3 Analyzer (`/agent/analyzer`)

**Función**: Enriquecer datos y generar alertas

**Módulos**:
- `geo_locator.py`: Geolocalización de IPs
  - Base de datos MaxMind GeoLite2
  - Lookup offline (no requiere internet)
  - Retorna país, ciudad, coordenadas

- `behavior_profiler.py`: Detección de anomalías
  - Baseline de comportamiento "normal"
  - Detección de:
    - Conexiones a horas inusuales (3-6 AM)
    - Volúmenes anormales de datos
    - Destinos inesperados (ej. cámara → China)

- `reputation_checker.py`: Verificación de IPs
  - Lista de rangos conocidos (AWS, Google, etc.)
  - Detección de IPs sospechosas

**Flujo de análisis**:
```
1. Nuevo flujo capturado
2. Geolocalizar IP destino → país, ciudad, lat/lon
3. Actualizar flujo con geo data
4. Calcular perfil de comportamiento del dispositivo
5. Comparar con baseline
6. Si anomalía detectada → generar alerta
7. Guardar alerta en DB
8. Broadcast via WebSocket
```

#### 3.4 FastAPI Server (`/agent/api`)

**Función**: API REST y WebSocket para el frontend

**Endpoints**:
```python
# Dispositivos
GET  /api/devices              # Lista de dispositivos
GET  /api/devices/{id}         # Detalle de dispositivo
GET  /api/devices/{id}/flows   # Flujos por dispositivo
GET  /api/devices/{id}/alerts  # Alertas por dispositivo

# Análisis geográfico
GET  /api/destinations         # Destinos agregados (para mapa)

# Alertas
GET  /api/alerts               # Todas las alertas
PUT  /api/alerts/{id}          # Marcar alerta como leída

# Estadísticas
GET  /api/stats                # Stats generales

# Salud
GET  /api/health               # Health check

# WebSocket
WS   /ws                       # Updates en tiempo real
```

**WebSocket**:
- Conexión persistente para updates en tiempo real
- Broadcast de:
  - Nuevos dispositivos descubiertos
  - Nuevas alertas generadas
  - Estadísticas actualizadas

**Servicio de archivos estáticos**:
```python
app.mount("/", StaticFiles(directory="dashboard/out", html=True))
```

---

### 4. Data Layer

#### 4.1 SQLite Database

**Ubicación**: `/data/iotsentry.db`

**Esquema**:

**Tabla `devices`**:
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY,
    mac_address TEXT UNIQUE NOT NULL,
    ip_address TEXT,
    hostname TEXT,
    vendor TEXT,
    device_type TEXT,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP
);
```

**Tabla `flows`**:
```sql
CREATE TABLE flows (
    id INTEGER PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    dest_ip TEXT NOT NULL,
    dest_port INTEGER,
    protocol TEXT,
    dest_country TEXT,
    dest_city TEXT,
    dest_lat REAL,
    dest_lon REAL,
    bytes_sent INTEGER,
    packets_sent INTEGER,
    timestamp TIMESTAMP
);
```

**Tabla `alerts`**:
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    device_id INTEGER REFERENCES devices(id),
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT,
    metadata JSON,
    timestamp TIMESTAMP,
    acknowledged BOOLEAN DEFAULT 0
);
```

**Índices**:
- `devices.mac_address` (único)
- `flows.device_id`
- `flows.timestamp`
- `alerts.device_id`
- `alerts.timestamp`

#### 4.2 Archivos de Datos

**GeoLite2 City Database** (`shared/databases/GeoLite2-City.mmdb`):
- Base de datos binaria de MaxMind
- Tamaño: ~70 MB
- Mapping: IP → País, Ciudad, Coordenadas
- Formato: MMDB (MaxMind DB)

**IEEE OUI Database** (`shared/databases/oui.txt`):
- Formato texto plano
- Tamaño: ~3 MB
- Mapping: MAC prefix (OUI) → Fabricante
- Formato: `XX-XX-XX   (hex)    VENDOR NAME`

---

## 🔄 Flujos de Datos Principales

### Flujo 1: Descubrimiento de Dispositivo

```
┌──────────────┐
│ User abre    │
│ aplicación   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Scanner inicia   │
│ escaneo ARP      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Dispositivos     │
│ detectados       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ OUI lookup       │
│ (fabricante)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Guardar en DB    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ WebSocket        │
│ broadcast        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Dashboard        │
│ actualiza lista  │
└──────────────────┘
```

### Flujo 2: Captura y Análisis de Tráfico

```
┌──────────────┐
│ Dispositivo  │
│ envía paquete│
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Sniffer captura  │
│ (Scapy)          │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Extraer metadata │
│ (IP, puerto)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Agregar a flujo  │
│ (flow_tracker)   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Geolocalizar IP  │
│ (GeoLite2)       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Analizar patrón  │
│ (behavior)       │
└──────┬───────────┘
       │
       ├─────────────┐
       │             │ (si anomalía)
       ▼             ▼
┌──────────────┐  ┌──────────────┐
│ Guardar flujo│  │ Crear alerta │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌──────────────────┐
       │ Dashboard        │
       │ muestra datos    │
       └──────────────────┘
```

### Flujo 3: Visualización en Dashboard

```
┌──────────────┐
│ User navega  │
│ a /devices   │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ HTTP GET         │
│ /api/devices     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ FastAPI query DB │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Serializar JSON  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Frontend recibe  │
│ y renderiza      │
└──────────────────┘
```

---

## 🔒 Consideraciones de Seguridad

### Privacidad por Diseño

1. **No captura contenido**: Solo headers de paquetes
2. **Todo local**: No envía datos a servidores externos
3. **Cifrado opcional**: Base de datos SQLite puede cifrarse (futuro)
4. **Open source**: Código auditable

### Permisos Requeridos

**Linux**:
- CAP_NET_RAW para captura de paquetes
- Solución: `setcap cap_net_raw+ep ./executable`

**macOS**:
- Root/sudo para acceso a interfaz de red
- Solución: Primera ejecución con sudo

**Windows**:
- Privilegios de administrador
- Npcap instalado
- Solución: "Ejecutar como administrador"

### Mitigaciones

- Validación de todas las entradas
- Sin eval() o exec() de datos externos
- Sanitización de datos en visualizaciones
- Rate limiting en API (futuro)

---

## 🚀 Performance

### Optimizaciones

**Scanner**:
- Timeout de 3 segundos para ARP
- Escaneo periódico (cada 5 minutos, configurable)
- Caché de dispositivos conocidos

**Sniffer**:
- Filtros BPF para reducir overhead
- Agregación de paquetes antes de DB write
- Buffer circular para flujos recientes

**Analyzer**:
- GeoIP lookup con caché LRU
- Procesamiento en background thread
- Batch inserts en base de datos

**Frontend**:
- Static generation (Next.js export)
- Lazy loading de componentes pesados
- Virtualización de listas largas (futuro)

### Recursos Estimados

- CPU: 5-10% en idle, 20-30% durante escaneo
- RAM: 150-300 MB
- Disco: 100 MB (app) + variable (datos capturados)
- Red: Mínimo (solo ARP + metadata)

---

## 📦 Empaquetado y Distribución

### PyInstaller Build

```
/dist
├── IoTSentry               # Ejecutable principal
├── dashboard/              # Static files Next.js
│   ├── _next/
│   ├── index.html
│   └── ...
└── databases/              # Bases de datos
    ├── GeoLite2-City.mmdb
    └── oui.txt
```

**Proceso**:
1. Next.js: `npm run build` → `/dashboard/out`
2. PyInstaller: `pyinstaller build.spec` → `/dist`
3. Bundle incluye: Python runtime, dependencies, dashboard, databases

**Tamaño del ejecutable**:
- Windows: ~80 MB
- macOS: ~75 MB
- Linux: ~70 MB

---

## 🔮 Extensibilidad

### Puntos de Extensión

1. **Nuevos tipos de dispositivos**: Añadir heurísticas en `device_identifier.py`
2. **Nuevos tipos de alertas**: Extender `behavior_profiler.py`
3. **Nuevas visualizaciones**: Añadir componentes React en `/dashboard/components`
4. **Nuevos endpoints API**: Añadir routes en `/agent/api/routes.py`
5. **Plugins**: Sistema de plugins (futuro)

### Roadmap Técnico

- [ ] Plugin system
- [ ] Machine learning para detección de anomalías
- [ ] Integración con iptables/pfctl (bloqueo activo)
- [ ] Mobile app companion
- [ ] Multi-usuario / Multi-red

---

## 📚 Referencias Técnicas

- [Scapy Documentation](https://scapy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- [IEEE OUI Database](https://standards.ieee.org/products-programs/regauth/oui/)

---

**Última actualización**: 2025-01-XX
