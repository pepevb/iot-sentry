# Guía de Desarrollo - IoT Sentry

Esta guía está dirigida a desarrolladores que quieren contribuir o modificar IoT Sentry.

## 🛠️ Configuración del Entorno de Desarrollo

### Requisitos Previos

- Python 3.10 o superior
- Node.js 18 o superior
- Git
- Editor de código (recomendado: VSCode)

### Instalación Paso a Paso

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/iot-sentry.git
cd iot-sentry
```

#### 2. Configurar Backend (Python)

```bash
# Crear entorno virtual
cd agent
python -m venv venv

# Activar entorno virtual
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install pytest pytest-asyncio black flake8 mypy
```

#### 3. Configurar Frontend (Next.js)

```bash
cd ../dashboard
npm install
```

#### 4. Descargar Bases de Datos

```bash
cd ../scripts
./download-geodata.sh
```

#### 5. Verificar Instalación

```bash
# Test del scanner
cd ../agent
python -m scanner.network_scanner

# Test del dashboard (modo desarrollo)
cd ../dashboard
npm run dev
# Abrir http://localhost:3000
```

---

## 🏃 Ejecutar en Modo Desarrollo

### Opción 1: Componentes Separados

**Terminal 1 - Backend API:**
```bash
cd agent
source venv/bin/activate
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend Dev Server:**
```bash
cd dashboard
npm run dev
# Se abre en http://localhost:3000
```

**Terminal 3 - Scanner (opcional):**
```bash
cd agent
source venv/bin/activate
python -m scanner.network_scanner
```

### Opción 2: Script de Desarrollo

```bash
# TODO: Crear script dev.sh que inicie todo
./scripts/dev.sh
```

---

## 📁 Estructura del Código

### Backend (Python)

```
/agent
├── scanner/
│   ├── network_scanner.py    # Escaneo ARP
│   ├── device_identifier.py  # Identificación de dispositivos
│   └── __init__.py
├── sniffer/
│   ├── packet_capture.py     # Captura de paquetes
│   ├── flow_tracker.py       # Tracking de flujos
│   └── __init__.py
├── analyzer/
│   ├── geo_locator.py        # Geolocalización
│   ├── behavior_profiler.py  # Detección de anomalías
│   ├── reputation_checker.py # Verificación de IPs
│   └── __init__.py
├── api/
│   ├── main.py               # FastAPI app
│   ├── routes.py             # Endpoints
│   ├── websocket.py          # WebSocket handler
│   └── __init__.py
└── database/
    ├── models.py             # SQLAlchemy models
    ├── database.py           # DB setup
    └── __init__.py
```

### Frontend (Next.js)

```
/dashboard
├── app/
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Dashboard principal
│   ├── devices/
│   │   ├── page.tsx          # Lista de dispositivos
│   │   └── [id]/
│   │       └── page.tsx      # Detalle de dispositivo
│   ├── map/
│   │   └── page.tsx          # Mapa mundial
│   └── alerts/
│       └── page.tsx          # Centro de alertas
├── components/
│   ├── DeviceCard.tsx
│   ├── WorldMap.tsx
│   ├── TrafficChart.tsx
│   ├── AlertCard.tsx
│   └── ui/                   # shadcn/ui components
└── lib/
    ├── api.ts                # Cliente API
    ├── utils.ts              # Utilidades
    └── types.ts              # TypeScript types
```

---

## 🧪 Testing

### Backend Tests

```bash
cd agent
pytest

# Con coverage
pytest --cov=. --cov-report=html

# Test específico
pytest tests/test_scanner.py
```

### Frontend Tests (TODO)

```bash
cd dashboard
npm run test

# E2E tests
npm run test:e2e
```

---

## 🎨 Code Style

### Python

Usamos **Black** para formateo y **Flake8** para linting:

```bash
# Formatear código
black agent/

# Linting
flake8 agent/

# Type checking
mypy agent/
```

**Configuración** (.flake8):
```ini
[flake8]
max-line-length = 100
exclude = venv/,.git/,__pycache__/
```

### TypeScript/React

Usamos **ESLint** y **Prettier**:

```bash
cd dashboard

# Lint
npm run lint

# Format
npm run format
```

---

## 🔨 Build Process

### Build Completo

```bash
./scripts/build.sh
```

### Build Manual

**1. Dashboard:**
```bash
cd dashboard
npm run build
# Output: dashboard/out/
```

**2. Ejecutable:**
```bash
# Crear spec file si no existe
pyi-makespec desktop/app.py

# Build con PyInstaller
pyinstaller desktop/build.spec

# Output: dist/IoTSentry
```

---

## 🐛 Debugging

### Backend (Python)

**Debug en VSCode:**

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["agent.api.main:app", "--reload"],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

**Debug prints:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Device found: {device}")
```

### Frontend (Next.js)

**Debug en navegador:**
- Chrome DevTools
- React Developer Tools

**Server-side:**
```typescript
console.log('Server data:', data)
```

---

## 📊 Database Migrations

```bash
# TODO: Configurar Alembic para migraciones

# Crear migración
alembic revision --autogenerate -m "Add new field"

# Aplicar migración
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🔌 API Development

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Get devices
curl http://localhost:8000/api/devices | jq

# Get device details
curl http://localhost:8000/api/devices/1 | jq

# WebSocket (usando wscat)
npm install -g wscat
wscat -c ws://localhost:8000/ws
```

### Añadir Nuevo Endpoint

1. **Definir modelo** (si necesario):
```python
# agent/database/models.py
class NewModel(Base):
    __tablename__ = 'new_table'
    id = Column(Integer, primary_key=True)
    # ...
```

2. **Crear endpoint**:
```python
# agent/api/routes.py
@router.get("/api/new-endpoint")
async def get_new_data(db: Session = Depends(get_db_session)):
    data = db.query(NewModel).all()
    return [item.to_dict() for item in data]
```

3. **Actualizar cliente**:
```typescript
// dashboard/lib/api.ts
async getNewData(): Promise<NewData[]> {
  const response = await fetch(`${this.baseURL}/api/new-endpoint`)
  return response.json()
}
```

---

## 🎨 Frontend Development

### Añadir Nuevo Componente

1. **Crear componente**:
```typescript
// dashboard/components/MyComponent.tsx
import { Card } from '@/components/ui/card'

export function MyComponent({ data }: { data: any }) {
  return (
    <Card>
      <h2>{data.title}</h2>
    </Card>
  )
}
```

2. **Usar en página**:
```typescript
// dashboard/app/page.tsx
import { MyComponent } from '@/components/MyComponent'

export default function Page() {
  return <MyComponent data={...} />
}
```

### Añadir Nueva Página

```bash
# Crear directorio y archivo
mkdir -p dashboard/app/nueva-seccion
touch dashboard/app/nueva-seccion/page.tsx
```

```typescript
// dashboard/app/nueva-seccion/page.tsx
export default function NuevaSeccion() {
  return (
    <div>
      <h1>Nueva Sección</h1>
    </div>
  )
}
```

Automáticamente disponible en `/nueva-seccion`

---

## 🔧 Utilidades de Desarrollo

### Scripts Útiles

**Limpiar builds:**
```bash
rm -rf dashboard/out/ dashboard/.next/ dist/ build/
```

**Reset database:**
```bash
rm data/iotsentry.db
# Se recrea automáticamente al iniciar
```

**Update dependencies:**
```bash
# Python
pip list --outdated
pip install -U <package>

# Node
npm outdated
npm update
```

---

## 📦 Release Process

### 1. Preparar Release

```bash
# Actualizar versión
# agent/__init__.py
__version__ = '1.1.0'

# dashboard/package.json
"version": "1.1.0"
```

### 2. Build

```bash
./scripts/build.sh
```

### 3. Testing

- Probar ejecutable en cada plataforma
- Verificar que no hay errores en consola
- Testing manual de funcionalidades principales

### 4. Tag y Release

```bash
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin v1.1.0
```

### 5. GitHub Release

- Subir ejecutables para cada plataforma
- Escribir changelog
- Marcar como latest release

---

## 🤝 Contribuir

### Workflow

1. **Fork** el repositorio
2. **Crear rama** para tu feature:
   ```bash
   git checkout -b feature/mi-feature
   ```
3. **Desarrollar** y **commitear**:
   ```bash
   git commit -m "feat: añadir nueva funcionalidad"
   ```
4. **Push** y crear **Pull Request**

### Commit Messages

Seguir [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: añadir soporte para IPv6
fix: corregir crash al escanear red grande
docs: actualizar guía de instalación
style: formatear código con black
refactor: simplificar lógica de scanner
test: añadir tests para analyzer
chore: actualizar dependencias
```

---

## 🐞 Debugging Common Issues

### "Permission denied" al ejecutar scanner

```bash
# Linux
sudo setcap cap_net_raw+ep $(which python3)

# macOS/Windows
# Ejecutar como administrador
```

### "Database locked"

```bash
# Cerrar todas las instancias de la app
pkill -f "python.*iot-sentry"

# Si persiste, eliminar lock
rm data/iotsentry.db-journal
```

### "Module not found"

```bash
# Verificar que estás en el entorno virtual
which python
# Debe apuntar a venv/bin/python

# Reinstalar dependencias
pip install -r requirements.txt
```

### Next.js build errors

```bash
# Limpiar caché
rm -rf .next/ out/

# Reinstalar node_modules
rm -rf node_modules/
npm install

# Rebuild
npm run build
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [Python](https://docs.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Scapy](https://scapy.readthedocs.io/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Next.js](https://nextjs.org/docs)
- [React](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### Libros y Tutoriales

- "Black Hat Python" - Justin Seitz
- "Violent Python" - TJ O'Connor
- "Network Programming with Python" - Dr. M. O. Faruque Sarker

---

## 💡 Ideas para Contribuir

### Features Fáciles (Good First Issues)

- [ ] Añadir más tipos de dispositivos a heurísticas
- [ ] Mejorar iconografía de dispositivos
- [ ] Traducir interfaz a otros idiomas
- [ ] Añadir dark/light mode toggle
- [ ] Exportar reportes a PDF

### Features Intermedias

- [ ] Implementar sistema de plugins
- [ ] Añadir gráficos de tendencias temporales
- [ ] Configuración de intervalos de escaneo
- [ ] Filtros avanzados en alertas
- [ ] Notificaciones desktop

### Features Avanzadas

- [ ] Machine learning para detección de anomalías
- [ ] Integración con iptables/pfctl (bloqueo)
- [ ] Multi-red monitoring
- [ ] API REST pública (para integraciones)
- [ ] Mobile app companion

---

**Última actualización**: 2025-01-XX
