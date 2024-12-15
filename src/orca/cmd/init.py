from os import sep

from ..options import OrcaOptions
from ..utils import fs 

def init(options : OrcaOptions) -> bool:
  if options['command']['name'] != "init":
    raise Exception("init: invalid options")

  project_dir = options["command"]["project_dir"]

  orcarc_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{project_dir}{sep}.orcarc", ["", ".json", ".jsonc"]))

  if not orcarc_file_path is None:
    raise Exception(f"{project_dir} is already an initialized orca project template")
  
  orcarc_file_path = f"{project_dir}{sep}.orcarc.json"

  with open(orcarc_file_path, "w") as fd:
    fd.write("""{
  "$schema": "https://raw.githubusercontent.com/LasramR/template-cloner/refs/heads/main/orcarc.schema.json"
}""")
  
  options["logger"].success(f"initialized new orca project template in {project_dir}")

  return True
