from os.path import basename, isdir, exists
from re import finditer, sub
from threading import Lock, Thread
from shutil import move
from typing import Set, List, Dict, Literal, Tuple

from .template import extract_variable_name_regex
from ..utils.config import MimicConfig, MimicVariable, overwrite_mimic_config
from ..utils.fs import ignore_glob

class MimicIssueReference:

  def __init__(self, name: str, source_path: str, line : int = 0, is_directory : bool = False, is_file = False):
    self.name = name
    self.source_path = source_path
    self.line = line
    self.is_directory = is_directory
    self.is_file = is_file

class MimicUnfixableIssue:

  def __init__(self, issue : MimicIssueReference, reason : str):
    self.issue = issue
    self.reason = reason

def _get_variables_from(template : str) -> Set[str] :
  return {match.group("variable_name") for match in finditer(extract_variable_name_regex, template)}

def _get_variables_from_file(source_file_path : str, variables : Set[MimicIssueReference], variables_lock : Lock) -> None :
  try:
    source_variables : Set[MimicIssueReference] = set()
    with open(source_file_path, "r") as fd:
      lineno = 1
      for line in fd:
        striped_line = line.strip()
        for v in _get_variables_from(striped_line):
          source_variables.add(MimicIssueReference(v, source_file_path, lineno))
        lineno += 1
      
    for v in _get_variables_from(basename(source_file_path)):
      source_variables.add(MimicIssueReference(v, source_file_path, is_file=True))
    
    with variables_lock:
      for v in source_variables:
        variables.add(v)
  except Exception:
    pass

def get_issues_from_mimic_template(mimic_template_dir : str, mimic_config : MimicConfig) -> Tuple[List[MimicIssueReference], List[str]]:
  variables : Set[MimicIssueReference] = set()
  variables_lock = Lock()
  get_variables_threads = []

  for source_path in ignore_glob(mimic_config.template.ignorePatterns, root_dir=mimic_template_dir, include_hidden=True):
    if isdir(source_path):
      for v in _get_variables_from(source_path):
        variables.add(MimicIssueReference(v, source_path, is_directory=True))
    else:
      source_file_get_variables_thread = Thread(
        target=_get_variables_from_file, args=(source_path, variables, variables_lock)
      )
      get_variables_threads.append(source_file_get_variables_thread)
      source_file_get_variables_thread.start()

  for t in get_variables_threads:
    t.join()
  
  reference_table = {k : [] for k in mimic_config.template.variables.keys()}

  undeclared_variables : List[MimicIssueReference]= []
  for v in variables:
    if v.name in reference_table:
      reference_table[v.name].append(v)
    else:
      undeclared_variables.append(v)
  
  unreferenced_variables : List[str] = []
  for k in reference_table.keys():
    if len(reference_table[k]) == 0:
      unreferenced_variables.append(k)

  return (undeclared_variables, unreferenced_variables)

def _escape_undefined_variables(template: str, variables : Dict[str, MimicVariable], fix_strategy : Literal["escape", "clear"]) -> str:
  def _escape_if_undefined(match):
    variable_name = match.group("variable_name")

    if variables.get(variable_name, None) != None:
      return f"{{{{ {variable_name} }}}}"
    
    if fix_strategy == "escape":
      return f"{{{{{{{{ {variable_name} }}}}}}}}" # So much mustaches
    elif fix_strategy == "clear":
      return ""
    else:
      return ""

  return sub(extract_variable_name_regex, _escape_if_undefined, template)

def _fix_issue_in_file(issue_file_path : str, variables : Dict[str, MimicVariable], fix_strategy : Literal["escape", "clear"]) -> None :
  try:
    with open(issue_file_path, "r") as fd:
      fixed_file_content = _escape_undefined_variables("".join(fd.readlines()), variables, fix_strategy)
    
    with open(issue_file_path, "w") as fd:
      fd.write(fixed_file_content)
  except:
    pass

def fix_issues_in_mimic_template(undeclared_variables : List[MimicIssueReference], unreferenced_variables : List[str], mimic_config_file_path : str, mimic_config : MimicConfig, fix_strategy : Literal["escape", "clear"]) -> List[MimicUnfixableIssue]:
  directory_issues : List[MimicIssueReference] = []
  file_name_issues : List[MimicIssueReference] = []
  content_issue_file_paths : Set[str] = set()
  
  while 0 < len(undeclared_variables):
    issue = undeclared_variables.pop()
    if issue.is_directory:
      directory_issues.append(issue)
    if issue.is_file:
      file_name_issues.append(issue)
    else:
      content_issue_file_paths.add(issue.source_path)

  file_content_fix_issue_threads : List[Thread] = []

  for issue_file_path in content_issue_file_paths:
    fix_issue_thread = Thread(
      target=_fix_issue_in_file,
      args=(issue_file_path, mimic_config.template.variables, fix_strategy)
    )
    file_content_fix_issue_threads.append(fix_issue_thread)
    fix_issue_thread.start()

  for t in file_content_fix_issue_threads:
    t.join()

  unfixable_issues : List[MimicUnfixableIssue] = []

  for issue in directory_issues:
    source_dir_path = issue.source_path
    fixed_dir_path = _escape_undefined_variables(source_dir_path, mimic_config.template.variables, fix_strategy)
    if exists(fixed_dir_path):
      unfixable_issues.append(MimicUnfixableIssue(issue, f"fixed dir path {fixed_dir_path} already exist"))
    elif len(fixed_dir_path.strip()) == 0:
      unfixable_issues.append(MimicUnfixableIssue(issue, f"fixed dir path contains empty dir name"))
    else:
      move(source_dir_path, fixed_dir_path)
  
  for issue in file_name_issues:
    source_file_path = issue.source_path
    fixed_file_path = _escape_undefined_variables(source_file_path, mimic_config.template.variables, fix_strategy)
    if exists(fixed_file_path):
      unfixable_issues.append(MimicUnfixableIssue(issue, f"fixed file path {fixed_file_path} already exist"))
    elif len(fixed_file_path.strip()) == 0:
      unfixable_issues.append(MimicUnfixableIssue(issue, f"fixed file path contains empty file name"))
    else:
      move(source_file_path, fixed_file_path)

  mimic_config_issue_count = len(unreferenced_variables)
  for variable_name in unreferenced_variables:
    if variable_name in mimic_config.template.variables:
      del mimic_config.template.variables[variable_name]
      del mimic_config.validated_raw["template"]["variables"][variable_name]
      unreferenced_variables.remove(variable_name)
  
  if mimic_config_issue_count != 0 and mimic_config_issue_count != len(unreferenced_variables):
    overwrite_mimic_config(mimic_config_file_path, mimic_config)

  return unfixable_issues
