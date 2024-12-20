from os import sep
from shutil import move
from typing import List

from ..utils import config, fs
from ..utils.logger import ColorTable, ColorReset
from ..actions.lint import get_issues_from_mimic_template, MimicIssueReference, fix_issues_in_mimic_template
from ..options import MimicOptions

def _print_lint_error(message : str) -> None :
  print(f"{ColorTable["YELLOW"]}{message}{ColorReset}")

def lint(options : MimicOptions) -> bool:
  if options['command']['name'] != "lint":
    raise Exception("lint: invalid options")
  
  mimic_template_dir = options["command"]["mimic_template_dir"]
  mimic_config_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{mimic_template_dir}{sep}.mimic", ["", ".json", ".jsonc"]))

  if mimic_config_file_path == None:
    options["logger"].warn(f"no .mimic(.json)? file has been found in {mimic_template_dir}: no more work to do. exiting")
    return True

  mimic_config_file_issues = config.is_mimic_config_file_data_valid(mimic_config_file_path)

  if len(mimic_config_file_issues):
    options["logger"].error(f"{mimic_config_file_path}: {len(mimic_config_file_issues)} error(s) found")
    for issue in mimic_config_file_issues:
      options["logger"].error(f"{issue.property} {issue.reason}")
    return False

  mimic_config = config.load_mimic_config(mimic_config_file_path)

  undeclared_variables, unreferenced_variables = get_issues_from_mimic_template(mimic_template_dir, mimic_config)

  if options["command"]["fix"] != None:
    initial_issue_count = len(undeclared_variables) + len(unreferenced_variables)
    if initial_issue_count == 0:
      options["logger"].success(f"no issue to fix in mimic template {mimic_template_dir}")
    else:
      unfixable_issue = fix_issues_in_mimic_template(undeclared_variables, unreferenced_variables, mimic_config_file_path, mimic_config, options["command"]["fix"])
      fixed_issue_count = initial_issue_count - len(unfixable_issue)
      options["logger"].success(f"fixed {fixed_issue_count}/{initial_issue_count} issue(s)")
      if len(unfixable_issue):
        options["logger"].error(f"could not fix {len(unfixable_issue)} issue(s):")      
        for unfixable in unfixable_issue:
          _print_lint_error(f"{unfixable.issue.source_path}: {unfixable.reason}")
        return False
  else:
    if 0 < len(undeclared_variables):
      options["logger"].info(f"there {'are' if 1 < len(undeclared_variables) else 'is'} {len(undeclared_variables)} variables in mimic template {mimic_template_dir} that {'are' if 1 < len(undeclared_variables) else 'is'} not defined in {mimic_config_file_path}")
      for uv in undeclared_variables:
        if uv.is_file:
          _print_lint_error(f"{uv.source_path}: {{{{ {uv.name} }}}} in file name but missing from .mimic.json")
        elif uv.is_directory:
          _print_lint_error(f"{uv.source_path}: {{{{ {uv.name} }}}} in directory name but missing from .mimic.json")
        else:
          _print_lint_error(f"{uv.source_path} line {uv.line}: {{{{ {uv.name} }}}} is missing from .mimic.json")

    if 0 < len(unreferenced_variables):
      options["logger"].info(f"{mimic_config_file_path}: {len(unreferenced_variables)} variable{'s are' if 1 < len(unreferenced_variables) else ' is'} declared but not used")
      for uv in unreferenced_variables:
        _print_lint_error(f"- {uv}")

  if 0 == len(undeclared_variables) + len(unreferenced_variables):
    options["logger"].success(f"{mimic_config_file_path}: no errors found")
  else:
    options["logger"].info("you can fix these issues with mimic lint --fix")
  return True
  