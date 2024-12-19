from os import sep
from typing import List

from ..utils import config, fs
from ..actions.lint import get_variables_from_mimic_template
from ..options import MimicOptions

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
    options["logger"].warn(f"{mimic_config_file_path}: {len(mimic_config_file_issues)} error(s) found")
    for issue in mimic_config_file_issues:
      options["logger"].error(f"{issue.property} {issue.reason}")
    return False

  mimic_config = config.load_mimic_config(mimic_config_file_path)

  reference_table = {k : [] for k in mimic_config.template.variables.keys()}
  undeclared_variables : List[config.MimicVariableReference]= []
  for v in get_variables_from_mimic_template(mimic_template_dir, mimic_config):
    if v.name in reference_table:
      reference_table[v.name].append(v)
    else:
      undeclared_variables.append(v)
  
  unreferenced_variables : List[str] = []
  for k in reference_table.keys():
    if len(reference_table[k]) == 0:
      unreferenced_variables.append(k)

  if 0 < len(unreferenced_variables):
    options["logger"].warn(f"{mimic_config_file_path}: {len(unreferenced_variables)} variable{'s are' if 1 < len(unreferenced_variables) else ' is'} declared but not used")
    for uv in unreferenced_variables:
      options["logger"].warn(f"- {uv}")

  if 0 < len(undeclared_variables):
    options["logger"].warn(f"There {'are' if 1 < len(undeclared_variables) else 'is'} {len(undeclared_variables)} variables in mimic_template {mimic_template_dir} which {'are' if 1 < len(undeclared_variables) else 'is'} not defined in {mimic_config_file_path}")
    for uv in undeclared_variables:
      if uv.is_file:
        options["logger"].warn(f"- file {uv.source_path} has a reference to {{{{{uv.name}}}}} in its name")
      elif uv.is_directory:
        options["logger"].warn(f"- directory {uv.source_path} has a reference to {{{{{uv.name}}}}} in its name")
      else:
        options["logger"].warn(f"- {{{{{uv.name}}}}} is declared in file {uv.source_path}")
    options["logger"].warn("These variables will be overwritten with an empty string during mimic_template creation")

  if 0 == len(undeclared_variables) + len(unreferenced_variables):
    options["logger"].success(f"{mimic_config_file_path}: no errors found")
  
  return True
  