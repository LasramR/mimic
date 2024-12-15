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

mimic_template_file_exts = [".mimict", ".mt"]

def get_file_from_template_file(file_path : str, template_file_exts : List[str] = mimic_template_file_exts) -> str :
    for e in template_file_exts:
        if file_path.endswith(e):
            return file_path.removesuffix(e)
    return file_path

def is_template_file(file_path : str, template_file_exts : List[str] = mimic_template_file_exts) -> bool :
  return any(map(lambda e : file_path.endswith(e), template_file_exts))

def remove_ignore(file_path : str) -> None :
  try:
      remove(file_path)
  except OSError:
      pass
