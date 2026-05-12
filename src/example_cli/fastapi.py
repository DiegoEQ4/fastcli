import os
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

  def new_project(self,name):
    path = Path.cwd()
    estructure = questionary.rawselect("Tipo de estructura: ", self.options_esctructure).ask()
    if estructure:
      index = self.options_esctructure.index(estructure)
      match index:
        case 0:
          self.layers_estructure(name)
      click.secho(f"Creando proyecto en: {path}")
      # os.makedirs(name,exist_ok=True)


  def layers_estructure(self, name):
    click.echo("Creando la estructura del proyecto")

    app_path = Path(name) / "app"
    click.secho(f"Creando: {app_path}")
    app_path.mkdir(parents=True, exist_ok=True)

    main_file = app_path / "main.py"
    click.secho(f"Creando: {main_file}")
    main_file.touch(exist_ok=True)

    for layer in self.layers:
        project_path = app_path / layer
        click.secho(f"Creando: {project_path}")
        (project_path / "__init__.py").touch()
        project_path.mkdir(parents=True, exist_ok=True)