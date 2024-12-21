from os import sep

from ..options import MimicOptions
from ..utils import fs 

def init(options : MimicOptions) -> bool:
  if options['command']['name'] != "init":
    raise Exception("init: invalid options")

  mimic_template_dir = options["command"]["mimic_template_dir"]

  mimic_config_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{mimic_template_dir}{sep}.mimic", ["", ".json", ".jsonc"]))

  if not mimic_config_file_path is None:
    raise Exception(f"{mimic_template_dir} is already an initialized mimic mimic_template template")
  
  mimic_config_file_path = f"{mimic_template_dir}{sep}.mimic.json"

  with open(mimic_config_file_path, "w") as fd:
    fd.write("""{
  "$schema": "https://raw.githubusercontent.com/LasramR/mimic/refs/heads/main/.mimic.0.5.1.schema.json",
  "git": {
    "enabled": false
  },
  "template": {
    "ignorePatterns": [".git", ".git/**"],
    "variables": {}
  },
  "hooks": []
}""")
  
  options["logger"].success(f"initialized new mimic mimic_template template in {mimic_template_dir}")

  return True
