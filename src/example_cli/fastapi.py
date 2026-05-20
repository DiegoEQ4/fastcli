import os
import sys
import subprocess
import re
import shutil
import click
import questionary
from pathlib import Path



class FastApiCli():

  options_esctructure = [
    "Layers",
    "Recommended for FastAPI"
  ]

  layers = [
    "services",
    "models",
    "routes"
  ]

  db_engines = [
    "SQLite",
    "PostgreSQL",
    "MySQL"
  ]

  db_urls = {
    "SQLite": "sqlite:///./database.db",
    "PostgreSQL": "postgresql://user:password@localhost:5432/dbname",
    "MySQL": "mysql+pymysql://user:password@localhost:3306/dbname"
  }

  db_packages = {
    "SQLite": "",
    "PostgreSQL": "psycopg2-binary",
    "MySQL": "pymysql"
  }

  def __self__():
    pass

  def is_valid_project(self) -> bool:
    app_dir = Path.cwd() / "app"
    main_file = app_dir / "main.py"
    return app_dir.exists() and main_file.exists()

  def generate_module(self, module_name: str):
    if not self.is_valid_project():
      click.secho("Error: No estás en la raíz de un proyecto FastAPI válido (no se encontró app/main.py).", fg="red")
      return

    app_dir = Path.cwd() / "app"
    
    services_layer = self.layers[0]
    models_layer = self.layers[1]
    routes_layer = self.layers[2]

    services_suffix = services_layer[:-1] if services_layer.endswith('s') else services_layer
    models_suffix = models_layer[:-1] if models_layer.endswith('s') else models_layer
    routes_suffix = routes_layer[:-1] if routes_layer.endswith('s') else routes_layer

    # Schemas
    schemas_dir = app_dir / "schemas"
    use_schemas = schemas_dir.exists()
    schemas_layer = "schemas"
    schemas_suffix = "schema"
    
    if use_schemas:
      schemas_file = app_dir / schemas_layer / f"{module_name}_{schemas_suffix}.py"
      if not schemas_file.exists():
        class_name_schema = f"{module_name.capitalize()}Schema"
        class_name = module_name.capitalize()
        schemas_file.write_text(
          f"from app.{models_layer}.{module_name}_{models_suffix} import {class_name}\n\n"
          f"class {class_name_schema}({class_name}):\n"
          f"    pass\n"
        )
        click.secho(f"Creado: {schemas_file}", fg="green")

    # Models
    models_file = app_dir / models_layer / f"{module_name}_{models_suffix}.py"
    if not models_file.parent.exists():
      models_file.parent.mkdir(parents=True, exist_ok=True)
      (models_file.parent / "__init__.py").touch()
      
    if not models_file.exists():
      class_name = module_name.capitalize()
      models_file.write_text(
        f"from typing import Optional\n"
        f"from sqlmodel import Field, SQLModel\n\n"
        f"class {class_name}(SQLModel, table=True):\n"
        f"    id: Optional[int] = Field(default=None, primary_key=True)\n"
        f"    name: str\n"
      )
      click.secho(f"Creado: {models_file}", fg="green")

    # Service
    service_file = app_dir / services_layer / f"{module_name}_{services_suffix}.py"
    if not service_file.parent.exists():
      service_file.parent.mkdir(parents=True, exist_ok=True)
      (service_file.parent / "__init__.py").touch()
      
    if not service_file.exists():
      class_name = module_name.capitalize()
      if use_schemas:
        class_name_schema = f"{class_name}Schema"
        service_file.write_text(
          f"from app.{schemas_layer}.{module_name}_{schemas_suffix} import {class_name_schema}\n\n"
          f"def get_{module_name}() -> list[{class_name_schema}]:\n"
          f"    return [{class_name_schema}(id=1, name=\"Item de ejemplo\")]\n"
        )
      else:
        service_file.write_text(
          f"from app.{models_layer}.{module_name}_{models_suffix} import {class_name}\n\n"
          f"def get_{module_name}() -> list[{class_name}]:\n"
          f"    return [{class_name}(id=1, name=\"Item de ejemplo\")]\n"
        )
      click.secho(f"Creado: {service_file}", fg="green")

    # Routes
    routes_file = app_dir / routes_layer / f"{module_name}_{routes_suffix}.py"
    if not routes_file.parent.exists():
      routes_file.parent.mkdir(parents=True, exist_ok=True)
      (routes_file.parent / "__init__.py").touch()
      
    if not routes_file.exists():
      if use_schemas:
        class_name_schema = f"{class_name}Schema"
        routes_file.write_text(
          f"from fastapi import APIRouter\n"
          f"from app.{services_layer}.{module_name}_{services_suffix} import get_{module_name}\n"
          f"from app.{schemas_layer}.{module_name}_{schemas_suffix} import {class_name_schema}\n\n"
          f"router = APIRouter(prefix=\"/{module_name}\", tags=[\"{module_name}\"])\n\n"
          f"@router.get('/', response_model=list[{class_name_schema}])\n"
          f"def read_{module_name}():\n"
          f"    return get_{module_name}()\n"
        )
      else:
        routes_file.write_text(
          f"from fastapi import APIRouter\n"
          f"from app.{services_layer}.{module_name}_{services_suffix} import get_{module_name}\n"
          f"from app.{models_layer}.{module_name}_{models_suffix} import {class_name}\n\n"
          f"router = APIRouter(prefix=\"/{module_name}\", tags=[\"{module_name}\"])\n\n"
          f"@router.get('/', response_model=list[{class_name}])\n"
          f"def read_{module_name}():\n"
          f"    return get_{module_name}()\n"
        )
      click.secho(f"Creado: {routes_file}", fg="green")

    # Inyectar en main.py
    main_file = app_dir / "main.py"
    if main_file.exists():
      content = main_file.read_text()
      
      # Evitar duplicados
      if f"from app.{routes_layer} import {module_name}_{routes_suffix}" not in content:
        # Añadir importación
        if "from fastapi import FastAPI" in content:
          content = content.replace(
            "from fastapi import FastAPI",
            f"from fastapi import FastAPI\nfrom app.{routes_layer} import {module_name}_{routes_suffix}"
          )
        
        # Añadir app.include_router
        if "app = FastAPI()" in content:
          content = content.replace(
            "app = FastAPI()",
            f"app = FastAPI()\n\napp.include_router({module_name}_{routes_suffix}.router)"
          )
        elif "app = FastAPI" in content: # caso general para atributos
          content = re.sub(
            r"(app\s*=\s*FastAPI\(.*?\))",
            rf"\1\n\napp.include_router({module_name}_{routes_suffix}.router)",
            content, count=1
          )
          
        main_file.write_text(content)
        click.secho(f"Ruta registrada en: {main_file}", fg="green")
      else:
        click.secho(f"La ruta ya estaba registrada en {main_file}", fg="yellow")

  def new_project(self, name, nodatabase=False):
    path = Path.cwd()
    project_path = Path(name)
    
    try:
      estructure = questionary.rawselect("Tipo de estructura: ", self.options_esctructure).ask()
      if estructure is None:
        click.secho("\nCreación cancelada.", fg="yellow")
        return
      
      db_engine = None
      if not nodatabase:
        db_engine = questionary.select("¿Qué motor de base de datos usarás?", self.db_engines).ask()
        if db_engine is None:
          click.secho("\nCreación cancelada.", fg="yellow")
          return
          
      index = self.options_esctructure.index(estructure)
      if index == 0:
        use_schemas = questionary.confirm("¿Deseas incluir la capa de schemas?").ask()
        if use_schemas is None:
          click.secho("\nCreación cancelada.", fg="yellow")
          return
      
      match index:
        case 0:
          self.layers_estructure(name, db_engine=db_engine, use_schemas=use_schemas)
        case 1:
          self.recommended_structure(name, db_engine=db_engine)
      click.secho(f"Creando proyecto en: {path}")
      
      project_path.mkdir(parents=True, exist_ok=True)
      
      # requirements.txt
      requirements = ["fastapi[standard]\n", "sqlmodel\n", "python-dotenv\n"]
      if db_engine and self.db_packages.get(db_engine):
        requirements.append(f"{self.db_packages[db_engine]}\n")
      elif nodatabase:
        requirements = ["fastapi[standard]\n"]
      
      req_file = project_path / "requirements.txt"
      click.secho(f"Creando archivo: {req_file}")
      req_file.write_text("".join(requirements))
      
      # .env
      if not nodatabase:
        env_file = project_path / ".env"
        click.secho(f"Creando archivo: {env_file}")
        if db_engine:
          env_file.write_text(f"DBHOST={self.db_urls[db_engine]}\n")
        else:
          env_file.write_text("# Sin base de datos configurada\n")
        
        # .env.example (template)
        env_example_file = project_path / ".env.example"
        click.secho(f"Creando archivo: {env_example_file}")
        if db_engine:
          env_example_file.write_text(f"DBHOST={self.db_urls[db_engine]}\n")
        else:
          env_example_file.write_text("# DBHOST=sqlite:///./database.db\n")
      
      # .gitignore
      gitignore_file = project_path / ".gitignore"
      click.secho(f"Creando archivo: {gitignore_file}")
      gitignore_content = (
        ".venv/\n"
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
        "!.env.example\n"
        "*.db\n"
      )
      gitignore_file.write_text(gitignore_content)
      
      # README
      readme_file = project_path / "README.md"
      click.secho(f"Creando archivo: {readme_file}")
      readme_content = f"# {name}\n\nProyecto base de FastAPI.\n\n## Instalación\n\n```bash\npip install -r requirements.txt\n```\n\n## Ejecución\n\n```bash\nfastapi dev app/main.py\n```\n"
      readme_file.write_text(readme_content)
      
      # Entorno virtual
      venv_path = project_path / ".venv"
      click.secho(f"Creando entorno virtual en: {venv_path}...", fg="green")
      subprocess.run([sys.executable, "-m", "venv", str(venv_path)])

      click.secho("Instalando dependencias en el entorno virtual...", fg="green")
      if os.name == 'nt':
          pip_exe = venv_path / "Scripts" / "pip.exe"
      else:
          pip_exe = venv_path / "bin" / "pip"

      subprocess.run([str(pip_exe), "install", "-r", str(req_file)])
      
      # Git init
      click.secho("Inicializando repositorio Git...", fg="green")
      subprocess.run(["git", "init", str(project_path)])

    except KeyboardInterrupt:
      click.secho("\n\nCreación cancelada por el usuario.", fg="yellow")
      if project_path.exists():
        click.secho(f"Eliminando carpeta parcial: {project_path}...", fg="yellow")
        shutil.rmtree(project_path)
        click.secho("Limpieza completada.", fg="yellow")


  def layers_estructure(self, name, db_engine=None, use_schemas=False):
    click.echo("Creando la estructura del proyecto")

    app_path = Path(name) / "app"
    click.secho(f"Creando: {app_path}")
    app_path.mkdir(parents=True, exist_ok=True)

    layers_to_create = self.layers.copy()
    if use_schemas:
      layers_to_create.append("schemas")

    for layer in layers_to_create:
      project_path = app_path / layer
      click.secho(f"Creando: {project_path}")
      project_path.mkdir(parents=True, exist_ok=True)
      (project_path / "__init__.py").touch()

    main_module = app_path / "__init__.py"
    main_file = app_path / "main.py"
    click.secho(f"Creando archivo principal: {main_file}")
    
    if db_engine:
      main_content = (
        "from contextlib import asynccontextmanager\n"
        "from fastapi import FastAPI\n"
        "from app.routes import user_routes\n"
        "from app.db import create_all_tables\n\n"
        "@asynccontextmanager\n"
        "async def lifespan(app: FastAPI):\n"
        "    create_all_tables()\n"
        "    yield\n\n"
        "app = FastAPI(lifespan=lifespan)\n\n"
        "app.include_router(user_routes.router)\n\n"
        "@app.get('/')\n"
        "def read_root():\n"
        "    return {'Hello': 'World'}\n"
      )
      
      # Crear db.py
      db_file = app_path / "db.py"
      click.secho(f"Creando archivo de base de datos: {db_file}", fg="green")
      db_content = (
        "import os\n\n"
        "from typing import Annotated\n"
        "from dotenv import load_dotenv\n"
        "from fastapi import Depends, FastAPI\n"
        "from sqlmodel import Session, create_engine, SQLModel\n\n"
        "load_dotenv()\n\n"
        "sqlite_url = os.getenv(\"DBHOST\")\n\n\n"
        "engine = create_engine(sqlite_url)\n\n"
        "def create_all_tables():\n"
        "  SQLModel.metadata.create_all(engine)\n\n"
        "def get_session():\n"
        "  with Session(engine) as session:\n"
        "    yield session\n\n\n"
        "SessionDep = Annotated[Session, Depends(get_session)]\n"
      )
      db_file.write_text(db_content)
    else:
      main_content = (
        "from fastapi import FastAPI\n"
        "from app.routes import user_routes\n\n"
        "app = FastAPI()\n\n"
        "app.include_router(user_routes.router)\n\n"
        "@app.get('/')\n"
        "def read_root():\n"
        "    return {'Hello': 'World'}\n"
      )
    
    main_file.write_text(main_content)
    main_module.write_text("")

    services_layer = self.layers[0]
    models_layer = self.layers[1]
    routes_layer = self.layers[2]

    services_suffix = services_layer[:-1] if services_layer.endswith('s') else services_layer
    models_suffix = models_layer[:-1] if models_layer.endswith('s') else models_layer
    routes_suffix = routes_layer[:-1] if routes_layer.endswith('s') else routes_layer

    # Crear archivos base en las capas con sus importaciones
    if use_schemas:
      schemas_layer = "schemas"
      schemas_suffix = "schema"
      schemas_file = app_path / schemas_layer / f"user_{schemas_suffix}.py"
      schemas_file.write_text(
          f"from app.{models_layer}.user_{models_suffix} import User\n\n"
          "class UserSchema(User):\n"
          "    pass\n"
      )

    models_file = app_path / models_layer / f"user_{models_suffix}.py"
    models_file.write_text(
        "from typing import Optional\n"
        "from sqlmodel import Field, SQLModel\n\n"
        "class User(SQLModel, table=True):\n"
        "    id: Optional[int] = Field(default=None, primary_key=True)\n"
        "    name: str\n"
    )

    service_file = app_path / services_layer / f"user_{services_suffix}.py"
    if use_schemas:
      service_file.write_text(
          f"from app.{schemas_layer}.user_{schemas_suffix} import UserSchema\n\n"
          "def get_users() -> list[UserSchema]:\n"
          "    return [UserSchema(id=1, name=\"Ejemplo\")]\n"
      )
    else:
      service_file.write_text(
          f"from app.{models_layer}.user_{models_suffix} import User\n\n"
          "def get_users() -> list[User]:\n"
          "    return [User(id=1, name=\"Ejemplo\")]\n"
      )

    routes_file = app_path / routes_layer / f"user_{routes_suffix}.py"
    if use_schemas:
      routes_file.write_text(
          "from fastapi import APIRouter\n"
          f"from app.{services_layer}.user_{services_suffix} import get_users\n"
          f"from app.{schemas_layer}.user_{schemas_suffix} import UserSchema\n\n"
          "router = APIRouter(prefix=\"/users\", tags=[\"users\"])\n\n"
          "@router.get('/', response_model=list[UserSchema])\n"
          "def read_users():\n"
          "    return get_users()\n"
      )
    else:
      routes_file.write_text(
          "from fastapi import APIRouter\n"
          f"from app.{services_layer}.user_{services_suffix} import get_users\n"
          f"from app.{models_layer}.user_{models_suffix} import User\n\n"
          "router = APIRouter(prefix=\"/users\", tags=[\"users\"])\n\n"
          "@router.get('/', response_model=list[User])\n"
          "def read_users():\n"
          "    return get_users()\n"
      )

  def recommended_structure(self, name, db_engine=None):
    click.echo("Creando la estructura recomendada por FastAPI")

    app_path = Path(name) / "app"
    click.secho(f"Creando: {app_path}")
    app_path.mkdir(parents=True, exist_ok=True)
    (app_path / "__init__.py").touch()
    
    # Subpackages
    routers_path = app_path / "routers"
    routers_path.mkdir(parents=True, exist_ok=True)
    (routers_path / "__init__.py").touch()
    
    internal_path = app_path / "internal"
    internal_path.mkdir(parents=True, exist_ok=True)
    (internal_path / "__init__.py").touch()
    
    # dependencies.py
    dependencies_file = app_path / "dependencies.py"
    dependencies_file.write_text(
        "from fastapi import Header, HTTPException\n\n"
        "async def get_token_header(x_token: str = Header(...)):\n"
        "    if x_token != \"fake-super-secret-token\":\n"
        "        raise HTTPException(status_code=400, detail=\"X-Token header invalid\")\n\n"
        "async def get_query_token(token: str):\n"
        "    if token != \"jessica\":\n"
        "        raise HTTPException(status_code=400, detail=\"No Jessica token provided\")\n"
    )
    
    # internal/admin.py
    admin_file = internal_path / "admin.py"
    admin_file.write_text(
        "from fastapi import APIRouter\n\n"
        "router = APIRouter()\n\n"
        "@router.post('/')\n"
        "async def update_admin():\n"
        "    return {\"message\": \"Admin getting schwifty\"}\n"
    )
    
    # routers/items.py
    items_file = routers_path / "items.py"
    items_file.write_text(
        "from fastapi import APIRouter, Depends, HTTPException\n"
        "from ..dependencies import get_token_header\n\n"
        "router = APIRouter(\n"
        "    prefix=\"/items\",\n"
        "    tags=[\"items\"],\n"
        "    dependencies=[Depends(get_token_header)],\n"
        "    responses={404: {\"description\": \"Not found\"}},\n"
        ")\n\n"
        "fake_items_db = {\"plumbus\": {\"name\": \"Plumbus\"}, \"gun\": {\"name\": \"Portal Gun\"}}\n\n"
        "@router.get('/')\n"
        "async def read_items():\n"
        "    return fake_items_db\n\n"
        "@router.get('/{item_id}')\n"
        "async def read_item(item_id: str):\n"
        "    if item_id not in fake_items_db:\n"
        "        raise HTTPException(status_code=404, detail=\"Item not found\")\n"
        "    return {\"name\": fake_items_db[item_id][\"name\"], \"item_id\": item_id}\n"
    )
    
    # routers/users.py
    users_file = routers_path / "users.py"
    users_file.write_text(
        "from fastapi import APIRouter\n\n"
        "router = APIRouter()\n\n"
        "@router.get('/users/', tags=['users'])\n"
        "async def read_users():\n"
        "    return [{\"username\": \"Rick\"}, {\"username\": \"Morty\"}]\n\n"
        "@router.get('/users/me', tags=['users'])\n"
        "async def read_user_me():\n"
        "    return {\"username\": \"fakecurrentuser\"}\n\n"
        "@router.get('/users/{username}', tags=['users'])\n"
        "async def read_user(username: str):\n"
        "    return {\"username\": username}\n"
    )
    
    # main.py
    main_file = app_path / "main.py"
    
    # If DB engine is present, we add db.py
    if db_engine:
      db_file = app_path / "db.py"
      click.secho(f"Creando archivo de base de datos: {db_file}", fg="green")
      db_content = (
        "import os\n\n"
        "from typing import Annotated\n"
        "from dotenv import load_dotenv\n"
        "from fastapi import Depends\n"
        "from sqlmodel import Session, create_engine, SQLModel\n\n"
        "load_dotenv()\n\n"
        "sqlite_url = os.getenv(\"DBHOST\")\n\n\n"
        "engine = create_engine(sqlite_url)\n\n"
        "def create_all_tables():\n"
        "  SQLModel.metadata.create_all(engine)\n\n"
        "def get_session():\n"
        "  with Session(engine) as session:\n"
        "    yield session\n\n\n"
        "SessionDep = Annotated[Session, Depends(get_session)]\n"
      )
      db_file.write_text(db_content)
      
      main_content = (
        "from contextlib import asynccontextmanager\n"
        "from fastapi import Depends, FastAPI\n"
        "from .dependencies import get_query_token, get_token_header\n"
        "from .internal import admin\n"
        "from .routers import items, users\n"
        "from .db import create_all_tables\n\n"
        "@asynccontextmanager\n"
        "async def lifespan(app: FastAPI):\n"
        "    create_all_tables()\n"
        "    yield\n\n"
        "app = FastAPI(dependencies=[Depends(get_query_token)], lifespan=lifespan)\n\n"
        "app.include_router(users.router)\n"
        "app.include_router(items.router)\n"
        "app.include_router(admin.router, prefix=\"/admin\", tags=[\"admin\"], dependencies=[Depends(get_token_header)], responses={418: {\"description\": \"I'm a teapot\"}})\n\n"
        "@app.get('/')\n"
        "async def root():\n"
        "    return {\"message\": \"Hello Bigger Applications!\"}\n"
      )
    else:
      main_content = (
        "from fastapi import Depends, FastAPI\n"
        "from .dependencies import get_query_token, get_token_header\n"
        "from .internal import admin\n"
        "from .routers import items, users\n\n"
        "app = FastAPI(dependencies=[Depends(get_query_token)])\n\n"
        "app.include_router(users.router)\n"
        "app.include_router(items.router)\n"
        "app.include_router(admin.router, prefix=\"/admin\", tags=[\"admin\"], dependencies=[Depends(get_token_header)], responses={418: {\"description\": \"I'm a teapot\"}})\n\n"
        "@app.get('/')\n"
        "async def root():\n"
        "    return {\"message\": \"Hello Bigger Applications!\"}\n"
      )
      
    main_file.write_text(main_content)