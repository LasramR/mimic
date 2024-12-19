from os import walk
from os.path import basename, join, isdir
from re import finditer
from threading import Lock, Thread
from typing import Set

from .template import extract_variable_name_regex
from ..utils.config import MimicVariableReference, MimicConfig
from ..utils.fs import ignore_glob

def _get_variables_from(template : str) -> Set[str] :
  return {match.group("variable_name") for match in finditer(extract_variable_name_regex, template)}

def _get_variables_from_file(source_file_path : str, variables : Set[MimicVariableReference], variables_lock : Lock) -> None :
  try:
    source_variables : Set[MimicVariableReference] = set()
    with open(source_file_path, "r") as fd:
      for v in _get_variables_from("".join(fd.readlines())):
        source_variables.add(MimicVariableReference(v, source_file_path))
    
    for v in _get_variables_from(basename(source_file_path)):
      source_variables.add(MimicVariableReference(v, source_file_path, is_file=True))
    
    with variables_lock:
      for v in source_variables:
        variables.add(v)
  except Exception:
    pass

def get_variables_from_mimic_template(mimic_template_dir : str, mimic_config : MimicConfig) -> Set[MimicVariableReference]:
  variables : Set[MimicVariableReference] = set()
  variables_lock = Lock()
  get_variables_threads = []

  for source_path in ignore_glob(mimic_config.template.ignorePatterns, root_dir=mimic_template_dir, include_hidden=True):
    if isdir(source_path):
      for v in _get_variables_from(source_path):
        variables.add(MimicVariableReference(v, source_path, is_directory=True))
    else:
      source_file_get_variables_thread = Thread(
        target=_get_variables_from_file, args=(source_path, variables, variables_lock)
      )
      get_variables_threads.append(source_file_get_variables_thread)
      source_file_get_variables_thread.start()

  for t in get_variables_threads:
    t.join()
  
  return variables
