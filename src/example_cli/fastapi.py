import os
import sys
import subprocess
import re
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

    # Models
    models_file = app_dir / models_layer / f"{module_name}_{models_suffix}.py"
    if not models_file.parent.exists():
      models_file.parent.mkdir(parents=True, exist_ok=True)
      (models_file.parent / "__init__.py").touch()
    
    if not models_file.exists():
      class_name = module_name.capitalize()
      models_file.write_text(
        f"from pydantic import BaseModel\n\n"
        f"class {class_name}(BaseModel):\n"
        f"    id: int\n"
        f"    name: str\n"
      )
      click.secho(f"Creado: {models_file}", fg="green")

    # Service
    service_file = app_dir / services_layer / f"{module_name}_{services_suffix}.py"
    if not service_file.parent.exists():
      service_file.parent.mkdir(parents=True, exist_ok=True)
      (service_file.parent / "__init__.py").touch()
      
    if not service_file.exists():
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
    estructure = questionary.rawselect("Tipo de estructura: ", self.options_esctructure).ask()
    
    db_engine = None
    if not nodatabase:
      db_engine = questionary.select("¿Qué motor de base de datos usarás?", self.db_engines).ask()
    
    if estructure:
      index = self.options_esctructure.index(estructure)
      match index:
        case 0:
          self.layers_estructure(name, db_engine=db_engine)
      click.secho(f"Creando proyecto en: {path}")
      
      project_path = Path(name)
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


  def layers_estructure(self, name, db_engine=None):
    click.echo("Creando la estructura del proyecto")

    app_path = Path(name) / "app"
    click.secho(f"Creando: {app_path}")
    app_path.mkdir(parents=True, exist_ok=True)

    for layer in self.layers:
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
    models_file = app_path / models_layer / f"user_{models_suffix}.py"
    models_file.write_text(
        "from pydantic import BaseModel\n\n"
        "class User(BaseModel):\n"
        "    id: int\n"
        "    name: str\n"
    )

    service_file = app_path / services_layer / f"user_{services_suffix}.py"
    service_file.write_text(
        f"from app.{models_layer}.user_{models_suffix} import User\n\n"
        "def get_users() -> list[User]:\n"
        "    return [User(id=1, name=\"Ejemplo\")]\n"
    )

    routes_file = app_path / routes_layer / f"user_{routes_suffix}.py"
    routes_file.write_text(
        "from fastapi import APIRouter\n"
        f"from app.{services_layer}.user_{services_suffix} import get_users\n"
        f"from app.{models_layer}.user_{models_suffix} import User\n\n"
        "router = APIRouter(prefix=\"/users\", tags=[\"users\"])\n\n"
        "@router.get('/', response_model=list[User])\n"
        "def read_users():\n"
        "    return get_users()\n"
    )