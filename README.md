# Cueva de las Pavas

Base del monorepo para una aplicación de estimación de afluencia turística. Incluye dos servicios
FastAPI y una aplicación React, con dependencias instalables, herramientas de calidad y CI.

El alcance actual es la infraestructura de desarrollo: la web muestra una pantalla inicial y cada
servicio expone `/health`. La integración meteorológica, la puntuación, los modelos y migraciones
de base de datos, la autenticación y el despliegue en AWS se implementarán después.

## Estructura

```text
apps/web/                  React + TypeScript + Vite
services/clima/            FastAPI, paquete pavas-clima
services/afluencia/         FastAPI, paquete pavas-afluencia
.github/workflows/ci.yml   Validaciones en GitHub Actions
compose.yaml               PostgreSQL para desarrollo local
pyproject.toml             Workspace uv y configuración Python
package.json               Workspace Bun y comandos del monorepo
uv.lock / bun.lock         Dependencias resueltas de ambos ecosistemas
```

El [informe del primer avance](Avance_Cueva_de_las_Pavas.docx) conserva la propuesta funcional y de
arquitectura. Su contenido describe el sistema futuro; no es evidencia de funcionalidades ya
implementadas.

## Requisitos

- Bun **1.4.0**, fijado en `.bun-version` y `packageManager`.
- uv **0.11.x**, desde **0.11.16**. CI utiliza 0.11.16.
- Python **3.12**. uv puede instalarlo cuando no esté disponible.
- Node.js **24 LTS**, fijado en `.node-version`, para Vite y Vitest. Bun administra los paquetes y
  ejecuta los scripts; no se utiliza npm ni se genera `package-lock.json`.
- Docker con Compose, solo si se necesita PostgreSQL local.

## Empezar

Desde la raíz del repositorio:

```sh
bun run setup
cp .env.example .env
bun run dev
```

`setup` usa los lockfiles sin modificarlos y sincroniza todos los paquetes Python en `.venv`.
`dev` inicia los tres procesos; `Ctrl+C` los detiene juntos. El arranque no requiere PostgreSQL
ni credenciales de APIs porque todavía no hay conexiones externas.

| Proceso | Dirección |
| --- | --- |
| Web | http://127.0.0.1:5173 |
| Clima | http://127.0.0.1:8001/health |
| Afluencia | http://127.0.0.1:8002/health |
| OpenAPI Clima | http://127.0.0.1:8001/docs |
| OpenAPI Afluencia | http://127.0.0.1:8002/docs |

También se pueden iniciar por separado con `bun run dev:web`, `bun run dev:clima` y
`bun run dev:afluencia`. Los comandos Python incluyen `--all-packages` para mantener ambos
servicios disponibles en el entorno de desarrollo compartido.

## Calidad y construcción

```sh
bun run check           # Lint, formato, tipos, pruebas y builds
bun run lint            # Biome y Ruff, sin modificar archivos
bun run format          # Aplica formato y correcciones automáticas
bun run typecheck       # TypeScript estricto y mypy estricto
bun run test            # Vitest y pytest
bun run test:coverage   # Cobertura de la base actual
bun run build           # Web en apps/web/dist; paquetes Python en dist
```

Las pruebas de arranque verifican React en jsdom y el inicio de los servicios con configuración
independiente. La cobertura solo corresponde al esqueleto, no a una aplicación turística completa.
CI instala dependencias bloqueadas, ejecuta `check` y valida la configuración de Compose.

## PostgreSQL local

```sh
cp .env.example .env    # Solo la primera vez; conserva tus cambios posteriores
bun run db:up
bun run db:logs
bun run db:down
```

La base escucha únicamente en `127.0.0.1:5432` y utiliza un volumen persistente. `db:down`
detiene el contenedor y conserva el volumen. Las credenciales de ejemplo son exclusivamente para
desarrollo. No se conecta aún ningún servicio a PostgreSQL ni se crean tablas.

SQLAlchemy, Psycopg y Alembic están declarados en cada servicio para añadir persistencia más
adelante. Al implementar esa etapa, cada servicio tendrá su propio esquema, usuario y migraciones;
el usuario de Compose sirve para administrar la instancia local, no para compartir tablas.

Se puede comprobar la configuración sin iniciar Docker ni crear `.env`:

```sh
docker compose --env-file .env.example config --quiet
```

## Configuración y límites entre servicios

- Los servicios se empaquetan con estructura `src/` y nombres Python distintos.
- Cada servicio declara sus dependencias de ejecución en su `pyproject.toml`; uv comparte la
  resolución en un único lockfile, no el código de negocio.
- Las variables usan prefijos `CLIMA_` y `AFLUENCIA_`. Los scripts se ejecutan desde la raíz para
  cargar `.env`. En despliegues futuros se inyectarán variables de entorno directamente.
- `/health` comprueba que el proceso responde. No es un chequeo de disponibilidad de PostgreSQL
  ni de Open-Meteo.
- No importar un servicio desde el otro. Su integración futura será mediante HTTP.
- No crear un paquete compartido hasta que exista una necesidad concreta.
- La configuración Compose es para desarrollo, no para publicar el sistema en EC2.

## Cambiar dependencias

```sh
bun add --cwd apps/web --exact nombre-paquete
bun add --dev --exact nombre-herramienta
uv add --package pavas-clima --bounds minor nombre-paquete
uv add --package pavas-afluencia --bounds minor nombre-paquete
uv add --group dev --bounds minor nombre-herramienta
uv sync --locked --all-packages
```

Versionar los manifiestos y ambos lockfiles juntos. No versionar `.env`, `.venv`, `node_modules`,
las cachés ni las salidas de build. Las herramientas mantienen sus cachés bajo `.cache/`.

Referencias técnicas: [workspaces de uv](https://docs.astral.sh/uv/concepts/projects/workspaces/),
[workspaces de Bun](https://bun.com/docs/pm/workspaces),
[Vite](https://vite.dev/guide/) y [Biome](https://biomejs.dev/guides/getting-started/).
