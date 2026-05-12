import questionary

class Questions():

  name = ''
  def __self__():
    pass


  def presentation(self):
    answers = questionary.form(
      human = questionary.confirm("Eres un humano?", default = True),
      name = questionary.text("Dime tu nombre"),
    ).ask()

    print(answers)
