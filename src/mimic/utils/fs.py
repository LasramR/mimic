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

def get_file_without_extension(file_path : str, exts : List[str] = []) -> str :
    if len(exts) == 0:
      return file_path
    
    for e in exts:
      if file_path.endswith(e):
        return file_path.removesuffix(e)
    
    return file_path

def is_file_of_extension(file_path : str, exts : List[str] = []) -> bool :
  if len(exts) == 0:
    return True
  return any(map(lambda e : file_path.endswith(e), exts))

def remove_ignore(file_path : str) -> None :
  try:
    remove(file_path)
  except OSError:
    pass
