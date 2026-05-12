import click
import os
import questionary

from .questions import Questions
from .fastapi import FastApiCli
from pathlib import Path



question = Questions()
fastapicli = FastApiCli()


options_lenguajes = [
  "FastAPI",
  "Express"
]

@click.group()
def group_root():
  pass



@click.command()
@click.argument("name")
def new(name):
  lenguaje = questionary.select("¿Que marco de trabajo ocuparas?",options_lenguajes).ask()
  match lenguaje:
    case "FastAPI":
      fastapicli.new_project(name)
  return lenguaje


@click.command()
def hello():
  question.presentation()

@click.command()
@click.argument('name')
def bye(name):
  print(f"Adios {name}!")


group_root.add_command(new)
group_root.add_command(bye)

if __name__ == '__main__':
  group_root()