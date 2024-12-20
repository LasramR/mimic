from os import sep

from ..utils import fs, config, input
from ..utils.logger import ColorTable, ColorReset
from ..actions.preview import preview_mimic_template
from ..options import MimicOptions

def preview(options : MimicOptions) -> bool:
  if options['command']['name'] != "preview":
    raise Exception("preview: invalid options")
  
  mimic_template_dir = options["command"]["mimic_template_dir"]
  mimic_config_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{mimic_template_dir}{sep}.mimic", ["", ".json", ".jsonc"]))

  if mimic_config_file_path == None:
    options["logger"].warn(f"no .mimic(.json)? file has been found: no more work to do. exiting")
    return True

  mimic_config = config.load_mimic_config(mimic_config_file_path)

  if mimic_config == None:
    raise Exception(f"cloud not preview mimic template because of broken mimic config (see https://raw.githubusercontent.com/LasramR/mimic/refs/heads/main/.mimic.0.5.1.schema.json)")
  
  options["logger"].info(f"previewing mimic_template {mimic_template_dir}")
  variables = {}
  for v in mimic_config.template.variables.keys():
    mimic_variable = mimic_config.template.variables[v]
    variables[mimic_variable.name] = input.get_user_variable_input(mimic_variable)

  mimic_template_preview = preview_mimic_template(mimic_template_dir, mimic_config, variables)

  options["logger"].success(f"mimic_template preview generated")

  options["logger"].info(f"directory change(s) ({len(mimic_template_preview.directory_preview.keys())})")
  for k in mimic_template_preview.directory_preview.keys():
    print(f"{ColorTable['RED']}{k}{ColorReset} -> {ColorTable['GREEN']}{mimic_template_preview.directory_preview[k]}")

  options["logger"].info(f"file change(s) ({len(mimic_template_preview.file_preview.keys())})")
  for k in mimic_template_preview.file_preview.keys():
    print(f"{ColorTable['RED']}{k}{ColorReset} -> {ColorTable['GREEN']}{mimic_template_preview.file_preview[k]}")

  options["logger"].info(f"content change(s) ({sum([len(mimic_template_preview.file_content_preview[k]) for k in mimic_template_preview.file_content_preview.keys()])})")

  for k in mimic_template_preview.file_content_preview.keys():
    for c in mimic_template_preview.file_content_preview[k]:
      options["logger"].info(f"{k} line {c.line}")
      print(f"{ColorTable["RED"]}- {c.raw}{ColorReset}")
      print(f"{ColorTable["GREEN"]}- {c.parsed}{ColorReset}")

  for when in config.MimicHookWhen:
    hooks = mimic_config.get_hooks_when(when)
    options["logger"].info(f"\"{when}\" hook(s) that will trigger ({len(hooks)})")
    for i in range(len(hooks)):
      h = hooks[i]
      print(f"{ColorTable['GREEN']}{h.name or f'<unnamed hook {i}>'}:{ColorReset}")
      print(f"{ColorTable['GREEN']}{len(h.steps)} step(s){ColorReset}")
      for s in h.steps:
        print(f"{ColorTable["MAGENTA"]}\t- {s}{ColorReset}")
      if not h.ignore_error:
        print(f"{ColorTable['RED']}will fail if an error occurs{ColorReset}")
      if not h.ignore_user_skip:
        print(f"{ColorTable['RED']}will fail if user skip{ColorReset}")
