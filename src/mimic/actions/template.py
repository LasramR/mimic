from re import sub
from os.path import join, isdir, split
from shutil import move
from threading import Thread, Lock
from typing import Dict, Any

from ..utils.fs import remove_ignore, ignore_glob
from ..utils.config import MimicVariable, MimicConfig

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

    source_dir_path, source_file_name = split(source_file_path)
    parsed_file_path = join(source_dir_path, inject_variable(source_file_name, variables, variables_values))

    with open(parsed_file_path, "w") as fd:
      fd.write(parsed_file_content)
    
    if source_file_path != parsed_file_path:
      remove_ignore(source_file_path)

    with inject_file_results_lock:
      inject_file_results[source_file_path] = True
  except Exception:
    with inject_file_results_lock:
      inject_file_results[source_file_path] = False

def _inject_dir(source_dir : str, variables : Dict[str, MimicVariable], variables_values : Dict[str, Any]) -> bool:
  try:
    move(source_dir, inject_variable(source_dir, variables, variables_values))
    return True
  except:
    return False

def inject_mimic_template(mimic_template_dir : str, mimic_config : MimicConfig, variables_values : Dict[str, Any]) -> bool :
  inject_file_results = {}
  inject_file_results_lock = Lock()
  inject_file_threads = []

  for source_path in ignore_glob(mimic_config.template.ignorePatterns, root_dir=mimic_template_dir, include_hidden=True):
    if isdir(source_path):
      _inject_dir(source_path, mimic_config.template.variables, variables_values)
    else:
      # Directories are always returned first in a glob match
      # We need to update the source_dir_path as we injected dir before
      source_dir_path, source_file_name = split(source_path)
      source_file_path = join(inject_variable(source_dir_path, mimic_config.template.variables, variables_values), source_file_name)

      source_file_path_inject_file_thread = Thread(
        target=_inject_file,
        args=(source_file_path, mimic_config.template.variables, variables_values, inject_file_results, inject_file_results_lock)
      )
      inject_file_threads.append(source_file_path_inject_file_thread)
      source_file_path_inject_file_thread.start()

  for t in inject_file_threads:
    t.join()
  
  return all([inject_file_results[k] for k in inject_file_results.keys()])
