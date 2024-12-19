from re import sub, finditer
from os import walk, sep
from os.path import join, basename, dirname
from shutil import move
from threading import Thread, Lock
from typing import Dict, Any

from ..utils.fs import get_file_without_extension, remove_ignore, is_file_of_extension
from ..utils.config import MimicVariable

extract_variable_name_regex = r"(?<!\{\{)\{\{\s*(?P<variable_name>\w+)\s*\}\}(?!\}\})"
extract_escaped_variable_name_regex = r"\{\{\{\{\s*(?P<variable_name>\w+)\s*\}\}\}\}"

def inject_variable(template: str, variables : Dict[str, MimicVariable], variables_values : Dict[str, Any]) -> str:
  def _replace_variable(match):
    variable_name = match.group("variable_name")

    if corresponding_variable := variables.get(variable_name, None):
      user_value = variables_values.get(variable_name, "")
      return corresponding_variable.format_variable_value(user_value) if not user_value is None else ""
    
    return ""
  
  def _escape_variable(match):
      variable_name = match.group("variable_name")
      return "{{ " + variable_name + " }}"

  template_with_replaced_variables = sub(extract_variable_name_regex, _replace_variable, template)
  return sub(extract_escaped_variable_name_regex, _escape_variable, template_with_replaced_variables)

def _inject_file(source_file_path : str, variables : Dict[str, MimicVariable], variables_values : Dict[str, Any], inject_file_results : Dict[str, bool], inject_file_results_lock : Lock) -> None :
  try:
    with open(source_file_path, "r") as fd:
      parsed_file_content = inject_variable("".join(fd.readlines()), variables, variables_values)

    parsed_file_path = join(dirname(source_file_path), get_file_without_extension(inject_variable(basename(source_file_path), variables, variables_values)))

    with open(parsed_file_path, "w") as fd:
      fd.write(parsed_file_content)
    
    if source_file_path != parsed_file_path:
      remove_ignore(source_file_path)

    with inject_file_results_lock:
      inject_file_results[source_file_path] = True
  except:
    with inject_file_results_lock:
      inject_file_results[source_file_path] = False

def _inject_dir(source_dir : str, variables : Dict[str, MimicVariable], variables_values : Dict[str, Any]) -> bool:
  try:
    move(source_dir, get_file_without_extension(inject_variable(source_dir, variables, variables_values)))
    return True
  except:
    return False

def inject_mimic_template(mimic_template_dir : str, variables : Dict[str, MimicVariable], variables_values : Dict[str, Any]) -> bool :
  template_file_paths = []

  for root, dirnames, filenames in walk(mimic_template_dir):
    for dirname in dirnames:
      if is_file_of_extension(dirname):
        if not _inject_dir(join(root, dirname), variables, variables_values):
          return False

  for root, dirnames, filenames in walk(mimic_template_dir):
    for filename in filenames:
      if is_file_of_extension(filename):
        template_file_paths.append(join(root, filename))
    
  inject_file_results = {}
  inject_file_results_lock = Lock()
  inject_threads = [
    Thread(target=_inject_file, args=(source_file_path, variables, variables_values, inject_file_results, inject_file_results_lock)) for source_file_path in template_file_paths
  ]
  for t in inject_threads:
    t.start()
  for t in inject_threads:
    t.join()
  
  return all([inject_file_results[k] for k in inject_file_results.keys()])
