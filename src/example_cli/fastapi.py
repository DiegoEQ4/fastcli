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
    "service",
    "models",
    "routes"
  ]

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
    
    # Models
    models_file = app_dir / "models" / f"{module_name}_models.py"
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
    service_file = app_dir / "service" / f"{module_name}_service.py"
    if not service_file.parent.exists():
      service_file.parent.mkdir(parents=True, exist_ok=True)
      (service_file.parent / "__init__.py").touch()
      
    if not service_file.exists():
      service_file.write_text(
        f"from app.models.{module_name}_models import {class_name}\n\n"
        f"def get_{module_name}() -> list[{class_name}]:\n"
        f"    return [{class_name}(id=1, name=\"Item de ejemplo\")]\n"
      )
      click.secho(f"Creado: {service_file}", fg="green")

    # Routes
    routes_file = app_dir / "routes" / f"{module_name}_routes.py"
    if not routes_file.parent.exists():
      routes_file.parent.mkdir(parents=True, exist_ok=True)
      (routes_file.parent / "__init__.py").touch()
      
    if not routes_file.exists():
      routes_file.write_text(
        f"from fastapi import APIRouter\n"
        f"from app.service.{module_name}_service import get_{module_name}\n"
        f"from app.models.{module_name}_models import {class_name}\n\n"
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
      if f"from app.routes import {module_name}_routes" not in content:
        # Añadir importación
        if "from fastapi import FastAPI" in content:
          content = content.replace(
            "from fastapi import FastAPI",
            f"from fastapi import FastAPI\nfrom app.routes import {module_name}_routes"
          )
        
        # Añadir app.include_router
        if "app = FastAPI()" in content:
          content = content.replace(
            "app = FastAPI()",
            f"app = FastAPI()\n\napp.include_router({module_name}_routes.router)"
          )
        elif "app = FastAPI" in content: # caso general para atributos
          content = re.sub(
            r"(app\s*=\s*FastAPI\(.*?\))",
            rf"\1\n\napp.include_router({module_name}_routes.router)",
            content, count=1
          )
          
        main_file.write_text(content)
        click.secho(f"Ruta registrada en: {main_file}", fg="green")
      else:
        click.secho(f"La ruta ya estaba registrada en {main_file}", fg="yellow")

  def new_project(self,name):
    path = Path.cwd()
    estructure = questionary.rawselect("Tipo de estructura: ", self.options_esctructure).ask()
    if estructure:
      index = self.options_esctructure.index(estructure)
      match index:
        case 0:
          self.layers_estructure(name)
      click.secho(f"Creando proyecto en: {path}")
      
      project_path = Path(name)
      project_path.mkdir(parents=True, exist_ok=True)
      
      req_file = project_path / "requirements.txt"
      click.secho(f"Creando archivo: {req_file}")
      req_file.write_text("fastapi[standard]\n")
      
      readme_file = project_path / "README.md"
      click.secho(f"Creando archivo: {readme_file}")
      readme_content = f"# {name}\n\nProyecto base de FastAPI.\n\n## Instalación\n\n```bash\npip install -r requirements.txt\n```\n\n## Ejecución\n\n```bash\nfastapi dev app/main.py\n```\n"
      readme_file.write_text(readme_content)
      
      venv_path = project_path / ".venv"
      click.secho(f"Creando entorno virtual en: {venv_path}...", fg="green")
      subprocess.run([sys.executable, "-m", "venv", str(venv_path)])

      click.secho("Instalando dependencias de FastAPI con fastapi[standard] en el entorno virtual...", fg="green")
      if os.name == 'nt':
          pip_exe = venv_path / "Scripts" / "pip.exe"
      else:
          pip_exe = venv_path / "bin" / "pip"

      subprocess.run([str(pip_exe), "install", "fastapi[standard]"])


  def layers_estructure(self, name):
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

    # Crear archivos base en las capas con sus importaciones
    models_file = app_path / "models" / "user_models.py"
    models_file.write_text(
        "from pydantic import BaseModel\n\n"
        "class User(BaseModel):\n"
        "    id: int\n"
        "    name: str\n"
    )

    service_file = app_path / "service" / "user_service.py"
    service_file.write_text(
        "from app.models.user_models import User\n\n"
        "def get_users() -> list[User]:\n"
        "    return [User(id=1, name=\"Ejemplo\")]\n"
    )

    routes_file = app_path / "routes" / "user_routes.py"
    routes_file.write_text(
        "from fastapi import APIRouter\n"
        "from app.service.user_service import get_users\n"
        "from app.models.user_models import User\n\n"
        "router = APIRouter(prefix=\"/users\", tags=[\"users\"])\n\n"
        "@router.get('/', response_model=list[User])\n"
        "def read_users():\n"
        "    return get_users()\n"
    )