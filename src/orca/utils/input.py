from re import match
from sys import stdout
from typing import Union, Any

from .config import OrcaVariable
from ..utils.logger import ColorTable, ColorReset

def check_valid_variable_input_type(variable : OrcaVariable, user_input : str) -> Union[Any, None] :
  match variable.type:
    case "boolean":
      if user_input.lower() == "true":
        return True
      elif user_input.lower() == "false":
        return False
    case "number":
      if not match(r"^-?\d+(\.\d+)?$", user_input) is None:
        return float(user_input)
    case "string":
      if len(user_input):
        return user_input
    case "regex":
      if not match(variable.item, user_input) is None:
        return user_input
    case "choice":
      try:
        i = int(user_input)
        if 0 <= i and i <= len(variable.item) - 1:
          return variable.item[i]
      except:
        return None
    case _:
      return None
  return None

def _get_variable_input_prompt(variable : OrcaVariable, show_constraints : bool) -> str :
  description = "" if variable.description == None else f"{variable.description}\n"
  
  constraints = ""
  
  if show_constraints and variable.type == "regex":
    constraints = f'must match "{variable.item}"\n'
  
  if variable.type == "choice":
    constraints = f"must be one of (specify index):\n"
    for i in range(len(variable.item)):
      constraints += f"[{i}] - {variable.item[i]}\n"

  required = "(skip empty) " if not variable.required else ""

  return f"{description}{constraints}{variable.name}: {required}"

def _clean_input_prompt(input_prompt : str, raw_user_input : str) -> None :
  lines = input_prompt.split("\n")

  for i in range(len(lines)):
    stdout.write("\033[F")
    stdout.write("\r")
    stdout.write(' ' * len(lines[len(lines) - 1 - i]))
    if i == 0:
      stdout.write(' ' * len(raw_user_input))
    stdout.flush()

  stdout.write("\r")
  stdout.flush()

def _clean_input_invalid_prompt(invalid_input_prompt : str) -> None :
  stdout.write("\r")
  stdout.write(' ' * len(invalid_input_prompt))

def get_user_variable_input(variable : OrcaVariable, show_constraints : bool = True) -> Union[Any, None] :
  input_prompt = _get_variable_input_prompt(variable, show_constraints)
  invalid_input_prompt = f"{ColorTable['RED']}invalid value, please retry{ColorReset}"

  retry = True
  hasRetry = False
  while retry:
    raw_user_input = input(input_prompt)

    if parsed_user_input := check_valid_variable_input_type(variable, raw_user_input.strip()):
      if hasRetry:
        _clean_input_invalid_prompt(invalid_input_prompt)
      _clean_input_prompt(input_prompt, raw_user_input)
      print(f"{ColorTable["MAGENTA"]}{variable.name}: {parsed_user_input}{ColorReset}")
      return parsed_user_input

    retry = variable.required

    if retry:
      print(invalid_input_prompt, end="")
      _clean_input_prompt(input_prompt, raw_user_input)

    hasRetry = True

  _clean_input_prompt(input_prompt, '')
  print(f"{ColorTable["MAGENTA"]}{variable.name}: <undefined>{ColorReset}")

  return None

def get_user_str_input(input_name : str, input_description : Union[str, None] = None, required : bool = True) -> Union[Any, None] :
  return get_user_variable_input(OrcaVariable.NewFrom(input_name, "string", required, input_description, None))

def get_user_confirmation(confirmation_prompt : str):
 return get_user_variable_input(OrcaVariable.NewFrom(confirmation_prompt, "regex", required=True, item=r"^[Yy]|[Nn]$"), show_constraints=False)
