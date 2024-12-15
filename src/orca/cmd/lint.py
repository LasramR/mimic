from os import sep
from typing import List

from ..utils import config, fs
from ..actions.template import get_variables_from_project
from ..options import OrcaOptions

def lint(options : OrcaOptions) -> bool:
  if options['command']['name'] != "lint":
    raise Exception("lint: invalid options")
  
  project_dir = options["command"]["project_dir"]
  orcarc_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{project_dir}{sep}.orcarc", ["", ".json", ".jsonc"]))

  if orcarc_file_path == None:
    options["logger"].warn(f"no orcarc(.json)? file has been found in {project_dir}: no more work to do. exiting")
    return True

  orcarc_issues = config.is_orcarc_data_valid(orcarc_file_path)

  if len(orcarc_issues):
    options["logger"].warn(f"{orcarc_file_path}: {len(orcarc_issues)} error(s) found")
    for issue in orcarc_issues:
      options["logger"].error(f"{issue.property} {issue.reason}")
    return False

  orcarc_config = config.load_orca_config(orcarc_file_path)

  reference_table = {k : [] for k in orcarc_config.template.variables.keys()}
  undeclared_variables : List[config.OrcaVariableReference]= []
  for v in get_variables_from_project(project_dir):
    if v.name in reference_table:
      reference_table[v.name].append(v)
    else:
      undeclared_variables.append(v)
  
  unreferenced_variables : List[str] = []
  for k in reference_table.keys():
    if len(reference_table[k]) == 0:
      unreferenced_variables.append(k)

  if 0 < len(unreferenced_variables):
    options["logger"].warn(f"{orcarc_file_path}: {len(unreferenced_variables)} variable(s) are declared but not used")
    for uv in unreferenced_variables:
      options["logger"].warn(f"- {uv}")

  if 0 < len(undeclared_variables):
    options["logger"].warn(f"There {len(undeclared_variables)} declared variables in project {project_dir} that are not defined in {orcarc_file_path}")
    for uv in undeclared_variables:
      if uv.is_file:
        options["logger"].warn(f"file {uv.source_path} has a reference to {{{uv.name}}} in its name")
      elif uv.is_directory:
        options["logger"].warn(f"directory {uv.source_path} has a reference to {{{uv.name}}} in its name")
      else:
        options["logger"].warn(f"{{{uv.name}}} is declared in file {uv.source_path}")
    options["logger"].warn("These variables will be overwritten with an empty string during project creation")

  if 0 == len(undeclared_variables) + len(unreferenced_variables):
    options["logger"].success(f"{orcarc_file_path}: no errors found")
  
  return True
  