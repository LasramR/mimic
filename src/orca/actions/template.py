from re import sub
from os import walk
from os.path import join
from shutil import move
from threading import Thread, Lock
from typing import Dict, Any

from ..utils.fs import get_file_from_template_file, remove_ignore, is_template_file

extract_variable_name_regex = r"{{\s*(?P<variable_name>\w+)\s*}}"
def _inject_variable(template: str, variables : Dict[str, Any]) -> str:
  def replace_variable(match):
    variable_name = match.group("variable_name")
    return str(variables.get(variable_name, "") or "")
  return sub(extract_variable_name_regex, replace_variable, template)

def parse_file(source_file_path: str, variables: Dict[str, Any]) -> str:
  with open(source_file_path, "r") as fd:
    return _inject_variable("".join(fd.readlines()), variables)

def _inject_file(source_file_path : str, variables : Dict[str, Any], inject_file_results : Dict[str, bool], inject_file_results_lock : Lock) -> None :
  try:
    parsed_file_content = parse_file(source_file_path, variables)

    parsed_file_path = get_file_from_template_file(_inject_variable(source_file_path, variables))

    with open(parsed_file_path, "w") as fd:
      fd.write(parsed_file_content)
    
    remove_ignore(source_file_path)

    with inject_file_results_lock:
      inject_file_results[source_file_path] = True
  except:
    with inject_file_results_lock:
      inject_file_results[source_file_path] = False

def _inject_dir(source_dir : str, variables : Dict[str, Any]) -> bool:
  try:
    move(source_dir, get_file_from_template_file(_inject_variable(source_dir, variables)))
    return True
  except:
    return False

def inject_project(project_dir : str, variables) -> bool :
  template_file_paths = []

  for root, dirnames, filenames in walk(project_dir):
    for dirname in dirnames:
      if is_template_file(dirname):
        if not _inject_dir(join(root, dirname), variables):
          return False

  for root, dirnames, filenames in walk(project_dir):
    for filename in filenames:
      if is_template_file(filename):
        template_file_paths.append(join(root, filename))
    
  inject_file_results = {}
  inject_file_results_lock = Lock()
  inject_threads = [
    Thread(target=_inject_file, args=(source_file_path, variables, inject_file_results, inject_file_results_lock)) for source_file_path in template_file_paths
  ]
  for t in inject_threads:
    t.start()
  for t in inject_threads:
    t.join()
  
  return all([inject_file_results[k] for k in inject_file_results.keys()])
