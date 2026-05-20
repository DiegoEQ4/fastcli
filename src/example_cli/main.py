import click
import os
import questionary

from .fastapi import FastApiCli
from pathlib import Path



question = Questions()
fastapicli = FastApiCli()


options_lenguajes = [
  "FastAPI",
  "Proximamente..."
]

@click.group()
def group_root():
  pass



@click.command()
@click.argument("name")
@click.option("--nodatabase", is_flag=True, default=False, help="No configurar base de datos.")
def new(name, nodatabase):
  """Genera un nuevo proyecto con las siguientes opciones
  """
  lenguaje = questionary.select("¿Que marco de trabajo ocuparas?",options_lenguajes).ask()
  match lenguaje:
    case "FastAPI":
      fastapicli.new_project(name, nodatabase=nodatabase)
  return lenguaje


@click.command()
def hello():
  question.presentation()

@click.command()
@click.argument('name')
def bye(name):
  print(f"Adios {name}!")

@click.command()
@click.argument('name')
def module(name):
  """Genera un nuevo módulo con sus capas (models, service, routes)."""
  fastapicli.generate_module(name)

group_root.add_command(new)
group_root.add_command(bye)
group_root.add_command(module)

if __name__ == '__main__':
  group_root()