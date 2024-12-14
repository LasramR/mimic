from re import match
from typing import Union, Any

from .config import OrcaVariable

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
    case _:
      return None
  return None

def get_user_variable_input(variable : OrcaVariable) -> Union[Any, None] :
  retry = True
  while retry:
    user_input = input(f"{'' if variable.description == None else f'{variable.description}, '}{variable.name}: {'(skip empty) ' if not variable.required else ''}").strip()

    if variable.required:
      if parsed_user_input := check_valid_variable_input_type(variable, user_input):
        return parsed_user_input

    retry = variable.required
  
  return None
