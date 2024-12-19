from os import remove, getcwd
from os.path import exists, abspath
from glob import glob
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

def ignoreGlob(ignorePatterns : List[str], root_dir : str = getcwd(), absolute_path : bool = False, include_hidden : bool = False) -> List[str]:
  ignoreMatchs = {}
  for pattern in ignorePatterns:
    for file_path in glob(pattern, root_dir=root_dir, include_hidden=include_hidden, recursive=True):
      ignoreMatchs[file_path] = True

  notIgnoredMatchs = []
  for file_path in glob("**", root_dir=root_dir, recursive=True, include_hidden=include_hidden):
    if file_path in ignoreMatchs:
      continue
    notIgnoredMatchs.append(abspath(file_path) if absolute_path else file_path)

  return notIgnoredMatchs
