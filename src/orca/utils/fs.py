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
