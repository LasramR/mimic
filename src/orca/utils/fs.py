from os import remove
from os.path import exists
from typing import List, Union

def resolve_existing_path(possible_paths : List[str]) -> Union[str, None]:
  for path in possible_paths:
    if exists(path):
      return path
  return None

def get_file_with_extensions(file_path : str, extensions : List[str]) -> List[str] :
  variants = []
  for ext in extensions:
    variants.append(f"{file_path}{ext}")
  return variants

orca_template_file_ext = ".ot"

def get_file_from_template_file(file_path : str, template_file_ext : str = orca_template_file_ext) -> str :
  return file_path.removesuffix(template_file_ext)

def is_template_file(file_path : str, template_file_ext : str = orca_template_file_ext) -> bool :
  return file_path.endswith(template_file_ext)

def remove_ignore(file_path : str) -> None :
  try:
      remove(file_path)
  except OSError:
      pass
