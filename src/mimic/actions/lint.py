from os.path import basename, isdir, exists
from re import finditer, sub
from threading import Lock, Thread
from shutil import move
from typing import Set, List, Dict

from .template import extract_variable_name_regex
from ..utils.config import MimicConfig, MimicVariable, overwrite_mimic_config
from ..utils.fs import ignore_glob

class MimicVariableReference:

  def __init__(self, name: str, source_path: str, line : int = 0, is_directory : bool = False, is_file = False):
    self.name = name
    self.source_path = source_path
    self.line = line
    self.is_directory = is_directory
    self.is_file = is_file

def _get_variables_from(template : str) -> Set[str] :
  return {match.group("variable_name") for match in finditer(extract_variable_name_regex, template)}

def _get_variables_from_file(source_file_path : str, variables : Set[MimicVariableReference], variables_lock : Lock) -> None :
  try:
    source_variables : Set[MimicVariableReference] = set()
    with open(source_file_path, "r") as fd:
      lineno = 1
      for line in fd:
        striped_line = line.strip()
        for v in _get_variables_from(striped_line):
          source_variables.add(MimicVariableReference(v, source_file_path, lineno))
        lineno += 1
      
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

def _escape_undefined_variables(template: str, variables : Dict[str, MimicVariable]) -> str:
  def _escape_if_undefined(match):
    variable_name = match.group("variable_name")

    if variables.get(variable_name, None) != None:
      return f"{{{{ {variable_name} }}}}"
    
    return f"{{{{{{{{ {variable_name} }}}}}}}}" # So much mustaches
  
  return sub(extract_variable_name_regex, _escape_if_undefined, template)

def _fix_issue(issue_file_path : str, variables : Dict[str, MimicVariable]) -> None :
  try:
    with open(issue_file_path, "r") as fd:
      fixed_file_content = _escape_undefined_variables("".join(fd.readlines()), variables)
    
    with open(issue_file_path, "w") as fd:
      fd.write(fixed_file_content)
  except:
    pass

def fix_mimic_template(undeclared_variables : List[MimicVariableReference], unreferenced_variables : List[str], mimic_config_file_path : str, mimic_config : MimicConfig) -> None:
  directory_issues : List[MimicVariableReference] = []
  file_name_issues : List[MimicVariableReference] = []
  content_issue_file_paths : Set[str] = set()

  file_content_fix_issue_threads : List[Thread] = []

  while 0 < len(undeclared_variables):
    issue = undeclared_variables.pop()
    if issue.is_directory:
      directory_issues.append(issue)
    if issue.is_file:
      file_name_issues.append(issue)
    else:
      content_issue_file_paths.add(issue.source_path)

  for issue_file_path in content_issue_file_paths:
    fix_issue_thread = Thread(
      target=_fix_issue,
      args=(issue_file_path, mimic_config.template.variables)
    )
    file_content_fix_issue_threads.append(fix_issue_thread)
    fix_issue_thread.start()

  for t in file_content_fix_issue_threads:
    t.join()

  for issue in directory_issues:
    source_dir_path = issue.source_path
    fixed_dir_path = _escape_undefined_variables(source_dir_path, mimic_config.template.variables)
    if exists(fixed_dir_path) or len(fixed_dir_path.strip()) == 0:
      undeclared_variables.append(issue)
      continue
    move(source_dir_path, fixed_dir_path)
  
  for issue in file_name_issues:
    source_file_path = issue.source_path
    fixed_file_path = _escape_undefined_variables(source_file_path, mimic_config.template.variables)
    if exists(fixed_file_path) or len(fixed_file_path.strip()) == 0:
      undeclared_variables.append(issue)
      continue
    move(source_file_path, fixed_file_path)

  mimic_config_issue_count = len(unreferenced_variables)
  for variable_name in unreferenced_variables:
    if variable_name in mimic_config.template.variables:
      del mimic_config.template.variables[variable_name]
      unreferenced_variables.remove(variable_name)
  
  if mimic_config_issue_count != 0 and mimic_config_issue_count != len(unreferenced_variables):
    overwrite_mimic_config(mimic_config_file_path, mimic_config)

  # TODO return reason why some fix failed
