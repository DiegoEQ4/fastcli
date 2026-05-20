# FastCLI (example-cli)

FastCLI es una herramienta de línea de comandos (CLI) desarrollada en Python y Click, diseñada para agilizar la creación y configuración de proyectos y módulos para FastAPI. Genera una arquitectura basada en capas de forma automática, configura entornos virtuales, bases de datos y registra las rutas.

## Características

- 🚀 **Generación de Proyectos**: Crea un proyecto FastAPI desde cero con una estructura de capas (`models`, `services`, `routes`).
- 🗄️ **Configuración de Base de Datos**: Soporta SQLite, PostgreSQL y MySQL (o puedes optar por no usar base de datos).
- 🧩 **Generación de Módulos**: Crea nuevas entidades (módulos) dentro de tu proyecto ya existente y auto-registra las rutas en tu `main.py`.
- ⚙️ **Configuración Automática**: Crea tu `.venv`, instala dependencias, crea el archivo `.env` e inicializa un repositorio de Git por defecto.

---

## 🛠️ Instalación

Puedes instalar esta herramienta utilizando `pip` o `pipx` (recomendado para aplicaciones CLI de Python, ya que crea entornos aislados).

### Usando pipx (Recomendado)

Si estás en la raíz del código fuente del CLI:

```bash
pipx install .
```

### Usando pip

Es altamente recomendable usar un entorno virtual, pero si deseas instalarlo globalmente o en tu entorno local:

```bash
pip install .
```

Si usas [Poetry](https://python-poetry.org/), también puedes instalar las dependencias y probar el script localmente:

```bash
poetry install
poetry run fastcli --help
```

---

## 💻 Comandos y Flujo de Uso

Una vez instalado, el comando principal es `fastcli`. A continuación se detallan los comandos disponibles.

### 1. Crear un Nuevo Proyecto

Crea la estructura base de un nuevo proyecto en FastAPI.

```bash
fastcli new <nombre_del_proyecto>
```

**Flujo:**
1. Te preguntará qué marco de trabajo utilizarás (actualmente enfocado en FastAPI).
2. Te pedirá elegir el tipo de estructura (Arquitectura por Capas recomendada).
3. Te preguntará qué motor de base de datos usar (SQLite, PostgreSQL, MySQL).
4. Automáticamente creará la carpeta del proyecto.
5. Generará la estructura: `app/models`, `app/services`, `app/routes` y `app/main.py`.
6. Generará el `.env` correspondiente y los `requirements.txt`.
7. Creará el entorno virtual (`.venv`), instalará las dependencias y finalmente inicializará `git`.

> **Nota:** Si no deseas configurar ninguna base de datos desde el inicio, puedes usar el flag `--nodatabase`:
> ```bash
> fastcli new <nombre_del_proyecto> --nodatabase
> ```

### 2. Generar un Nuevo Módulo

Permite crear una nueva entidad o módulo dentro de un proyecto previamente generado.

```bash
fastcli module <nombre_del_modulo>
```

**Importante a tomar en cuenta:**
- **Debes estar en la raíz del proyecto generado** (donde se encuentra la carpeta `app/` y el archivo `app/main.py`). El CLI validará la existencia de esta ruta.
- Al ejecutar este comando, se crearán tres archivos con código base, correspondientes a las capas:
  - `app/models/<nombre>_model.py`
  - `app/services/<nombre>_service.py`
  - `app/routes/<nombre>_route.py`
- El CLI automáticamente modificará tu archivo `app/main.py` para inyectar la nueva ruta (`app.include_router(...)`), por lo que no necesitas registrar el router manualmente.

### 3. Comandos de Utilidad

- **Ver el menú de ayuda:**
  ```bash
  fastcli --help
  ```

- **Comando de saludo (hello / bye):**
  ```bash
  fastcli hello
  fastcli bye <tu_nombre>
  ```

---

## 📌 Consideraciones al Trabajar con el Proyecto Generado

1. **Uso del Entorno Virtual:** 
   El proyecto generado ya contiene un `.venv`. Para activarlo en Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```
   En Windows:
   ```bash
   .venv\Scripts\activate
   ```

2. **Ejecución del Proyecto FastAPI:**
   Una vez generado tu proyecto, puedes levantarlo ubicándote en la carpeta del mismo y corriendo:
   ```bash
   fastapi dev app/main.py
   ```

3. **Arquitectura:**
   Mantén la lógica de negocio en la carpeta `services`, los modelos y esquemas en `models`, y los endpoints en `routes`. Cuando generes un nuevo módulo con `fastcli module`, la herramienta intentará respetar estos sufijos e importaciones.