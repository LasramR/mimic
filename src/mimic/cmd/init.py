from os import sep

from ..options import MimicOptions
from ..utils import fs 

def init(options : MimicOptions) -> bool:
  if options['command']['name'] != "init":
    raise Exception("init: invalid options")

  project_dir = options["command"]["project_dir"]

  mimic_config_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{project_dir}{sep}.mimic", ["", ".json", ".jsonc"]))

  if not mimic_config_file_path is None:
    raise Exception(f"{project_dir} is already an initialized mimic project template")
  
  mimic_config_file_path = f"{project_dir}{sep}.mimic.json"

  with open(mimic_config_file_path, "w") as fd:
    fd.write("""{
  "$schema": "https://raw.githubusercontent.com/LasramR/mimic/refs/heads/main/.mimic.schema.json",
  "git": {
    "enabled": false
  },
  "template": {
    "variables": {}
  },
  "hooks": []
}""")
  
  options["logger"].success(f"initialized new mimic project template in {project_dir}")

  return True
