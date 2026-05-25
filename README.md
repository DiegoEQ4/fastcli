# FastCLI (fastcli)

**FastCLI** es una herramienta de línea de comandos (CLI) interactiva, robusta y moderna desarrollada en Python con Click y Questionary, diseñada para agilizar y estandarizar la creación y configuración de proyectos y módulos para FastAPI. 

La herramienta genera automáticamente arquitecturas limpias, configura entornos virtuales, gestiona conexiones a bases de datos y registra rutas de forma dinámica.

---

## 🎨 Características Principales

- **🎨 Interfaz Atractiva e Interactiva**:
  - Incorpora un vistoso banner en formato **ASCII Art** con colores pastel al iniciar el asistente de creación.
  - Carga dinámicamente la versión y descripción del CLI desde los metadatos o el archivo `pyproject.toml`.
  - Utiliza menús interactivos fluidos y validados mediante `questionary` para guiar al desarrollador sin complicaciones.

- **📂 Múltiples Estructuras de Proyecto**:
  - **Layers (Arquitectura por Capas)**: La estructura modular clásica (`app/models`, `app/services`, `app/routes`). Permite opcionalmente incluir una capa de **schemas** (`app/schemas`) para separar y validar de forma limpia la entrada/salida de datos de las entidades de la base de datos.
  - **Recommended for FastAPI (Recomendada por FastAPI)**: Estructura orientada a aplicaciones grandes y escalables con paquetes específicos (`app/routers/` con subrutas como `items.py` y `users.py`, `app/internal/` para tareas de administración, `app/dependencies.py` para dependencias compartidas y `app/main.py`).

- **🗄️ Base de Datos e Integración con SQLModel**:
  - Configuración automatizada para **SQLite**, **PostgreSQL** y **MySQL**.
  - Si se configura una base de datos:
    - Se integra automáticamente con **SQLModel** (híbrido de SQLAlchemy y Pydantic).
    - Crea el archivo `app/db.py` con una sesión gestionada (`SessionDep`, `get_session`, `create_all_tables`).
    - Configura de forma transparente un gestor de ciclo de vida (`lifespan`) en `app/main.py` para asegurar que las tablas se creen de forma automática al arrancar el servidor de desarrollo.
    - Configura las variables de entorno de conexión en los archivos `.env` y `.env.example`.
  - Si se omite la base de datos (usando `--nodatabase` o seleccionándolo en el asistente):
    - Se genera una arquitectura limpia libre de código de base de datos.
    - Los modelos heredan directamente de `Pydantic BaseModel`.

- **⚙️ Inicialización Completa de Entorno**:
  - Creación automática del entorno virtual (`.venv`).
  - Instalación silenciosa de dependencias (`fastapi[standard]`, `sqlmodel`, `python-dotenv`, y conectores como `psycopg2-binary` o `pymysql` según la base de datos elegida).
  - Inicialización automática de un repositorio Git local junto con un archivo `.gitignore` adaptado para desarrollo en Python.

- **🛡️ Cancelación Segura (Clean Recovery)**:
  - En caso de interrumpir de forma abrupta el proceso interactivo (`Ctrl+C` / `KeyboardInterrupt`), FastCLI atrapa la interrupción y realiza una **limpieza total automática**, eliminando cualquier directorio o archivo temporal creado a medias para no dejar basura en el sistema.

- **🧪 Suite de Pruebas Unitarias Integrada**:
  - Cuenta con una suite de pruebas automatizadas escritas en **pytest** que aseguran la consistencia en la generación de arquitecturas (con y sin bases de datos, manejo de estructuras por capas, esquemas, y CLI general).

---

## 🛠️ Instalación

Puedes instalar FastCLI utilizando `pip`, `pipx` (recomendado para herramientas CLI globales, ya que crea entornos aislados) o a través de `Poetry` si estás en modo desarrollo.

### Usando pipx (Recomendado)

Si estás en la raíz del código fuente del proyecto CLI:

```bash
pipx install .
```

### Usando pip

Es altamente recomendable usar un entorno virtual, pero si deseas instalarlo localmente:

```bash
pip install .
```

### Usando Poetry (Entorno de Desarrollo)

Si deseas probar el script y realizar aportes locales, clona el proyecto y corre:

```bash
poetry install
poetry run fastcli --help
```

---

## 💻 Comandos y Flujo de Uso

Una vez instalado, el comando principal expuesto en tu sistema es `fastcli`.

### 1. Crear un Nuevo Proyecto

Crea la estructura base de un nuevo proyecto FastAPI adaptado a tus necesidades de forma 100% interactiva:

```bash
fastcli new <nombre_del_proyecto>
```

> [!NOTE]
> Si no deseas configurar ninguna base de datos desde el inicio, puedes saltarte esa parte en la selección interactiva o pasar de manera directa el flag `--nodatabase`:
> ```bash
> fastcli new <nombre_del_proyecto> --nodatabase
> ```

**Flujo interactivo paso a paso:**
1. **Marco de trabajo**: Selección del framework (actualmente enfocado en FastAPI).
2. **Estructura**: Elección entre `Layers` o `Recommended for FastAPI`.
3. **Schemas**: (Si elegiste `Layers`) Preguntará si deseas incluir la carpeta de schemas.
4. **Base de Datos**: Selección del motor (`SQLite`, `PostgreSQL`, `MySQL`).
5. **Generación**: Creación de carpetas, código base (`app/main.py`, `app/db.py`, etc.), `.env`, `.env.example`, `.gitignore`, `.venv` y posterior inicialización de git.

> [!IMPORTANT]
> Si en cualquiera de los pasos anteriores decides presionar `Ctrl+C` para cancelar la operación, FastCLI interceptará el evento e inmediatamente borrará el directorio del proyecto creado de forma parcial para mantener tu sistema limpio.

---

### 2. Generar un Nuevo Módulo

Permite crear una nueva entidad o módulo dentro de un proyecto previamente generado con FastCLI.

```bash
fastcli module <nombre_del_modulo>
```

> [!IMPORTANT]
> Debes ejecutar este comando situado en la **raíz del proyecto generado** (donde se encuentra la carpeta `app/` y el archivo `app/main.py`). El CLI validará la existencia del proyecto antes de generar código.

**Comportamiento Inteligente:**
- **Detección de Base de Datos**: El CLI busca la existencia de `app/db.py`. Si existe, asume que el proyecto usa base de datos y genera el modelo heredando de `SQLModel` configurado para tabla (`class MiModulo(SQLModel, table=True)`). Si no existe `db.py`, hereda de `Pydantic BaseModel`.
- **Detección de Schemas**: Si la estructura original incluía la capa opcional de `schemas` (detectado por la carpeta `app/schemas`), el comando crea automáticamente un archivo `<modulo>_schema.py` que hereda del modelo y actualiza las firmas y retornos en la capa de servicios y rutas para usar dicho esquema.
- **Auto-registro de Rutas**: Inyecta y registra de forma dinámica la nueva ruta (`app.include_router(...)`) y su importación en `app/main.py` de forma completamente automatizada sin requerir edición manual.

---

### 3. Comandos de Utilidad

- **Ver el menú de ayuda:**
  ```bash
  fastcli --help
  ```

- **Despedirse:**
  ```bash
  fastcli bye <tu_nombre>
  ```

---

## 🧪 Ejecución de Pruebas

Este proyecto implementa pruebas automatizadas para verificar que la generación de las arquitecturas se comporte según lo esperado. Las pruebas cubren la estructura de capas, la detección de base de datos y la funcionalidad de comandos Click.

Para ejecutar los tests utilizando **Poetry**:

```bash
poetry run pytest -v
```

O si tienes `pytest` instalado en tu entorno global:

```bash
pytest -v
```

---

## 📌 Consideraciones al Trabajar con el Proyecto Generado

1. **Uso del Entorno Virtual**: 
   El proyecto generado ya contiene un `.venv`. Para activarlo:
   - **Linux/Mac**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```

2. **Ejecución del Servidor**:
   Una vez levantado y activado el entorno, sitúate en la raíz del proyecto generado y arranca el servidor FastAPI:
   ```bash
   fastapi dev app/main.py
   ```

3. **Arquitectura modular**:
   - En la estructura de **Layers**, mantén la lógica de negocio en `services`, los modelos y entidades de base de datos en `models`, la validación de payloads en `schemas` (si se usa) y las rutas en `routes`.
   - En la estructura **Recomendada por FastAPI**, coloca tus routers en `routers/`, dependencias comunes en `dependencies.py` y rutas de administración/internas en `internal/`.