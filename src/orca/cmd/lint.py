from os import sep

from ..utils import config, fs
from ..options import OrcaOptions

def lint(options : OrcaOptions) -> bool:
  if options['command']['name'] != "lint":
    raise Exception("lint: invalid options")
  orcarc_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{options["command"]["project_dir"]}{sep}.orcarc", ["", ".json", ".jsonc"]))

  if orcarc_file_path == None:
    options["logger"].warn(f"no orcarc(.json)? file has been found: no more work to do. exiting")
    return True

  orcarc_issues = config.is_orcarc_data_valid(orcarc_file_path)

  if len(orcarc_issues):
    options["logger"].warn(f"{orcarc_file_path}: {len(orcarc_issues)} error(s) found")
    for issue in orcarc_issues:
      options["logger"].error(f"{issue.property} {issue.reason}")
    return False

  options["logger"].success(f"{orcarc_file_path}: no errors found")
  return True