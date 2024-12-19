from os import sep
from os.path import abspath, exists
from typing import Dict, Any

from ..actions.git import git_action
from ..actions.template import inject_mimic_template
from ..actions.hook import hook_action
from ..utils import git, cloning, fs, config, input, alias_wallet
from ..options import MimicOptions

def _run_hooks(mimic_template_dir : str, when : config.MimicHookWhenType, variables : Dict[str, config.MimicVariable], variables_values: Dict[str, Any], mimic_config : config.MimicConfig, options : MimicOptions) -> bool :
  hooks = mimic_config.get_hooks_when(when)
  options["logger"].info(f"running '{when}' hooks ({len(hooks)})")

  for h in hooks:
    hook_properties = []
    if h.ignore_user_skip:
      hook_properties.append("skippable")
    if h.ignore_error:
      hook_properties.append("error non fatal")
    hook_properties_log = f"({','.join(hook_properties)})" if len(hook_properties) else ''

    options["logger"].info(f"hook '{h.name or '<unnamed hook>'}'{hook_properties_log}")

    hook_result = True
    try:
      hook_result = hook_action(mimic_template_dir, h, variables, variables_values, options["command"]["unsafe_mode"])
    except Exception:
      if h.ignore_user_skip:
        options["logger"].warn(f"hook '{h.name or '<unnamed hook>'}' skipped")
      else:
        return False

    if not hook_result:
      if h.ignore_error:
        options["logger"].warn(f"hook '{h.name or '<unnamed hook>'}' failed but non fatal")
      else:
        return False
  return True

def clone(options : MimicOptions) -> bool :
  if options['command']["name"] != "clone":
    raise Exception("clone: invalid options")
  
  alias = options["command"]["mimic_uri"]
  mimic_uri = alias_wallet.resolve_alias_mimic_uri_from(options["command"]["alias_wallet_file_path"], alias)

  if alias != mimic_uri:
    options["logger"].info(f"{alias} has been resolved to {mimic_uri}")

  options["logger"].info(f"checking access to mimic {mimic_uri}")
  if not cloning.check_access_to_mimic_template(mimic_uri):
    raise Exception(f'could not resolve mimic {mimic_uri}. Are you sure that you have access to the mimic ?')

  options["logger"].success(f"ok")

  mimic_template_dir = options["command"].get("out_dir") or abspath(git.repository_name(mimic_uri))

  if exists(mimic_template_dir):
    raise Exception(f"out_dir {mimic_template_dir} already exist and cloning into it will fail. cancelling")

  options["logger"].info(f"cloning {mimic_uri} in {mimic_template_dir}")
  if not cloning.clone_mimic_template(mimic_uri, mimic_template_dir):
    raise Exception(f'could not clone mimic at "{mimic_template_dir}"')

  options["logger"].success(f"{mimic_uri} cloned")


  mimic_config_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{mimic_template_dir}{sep}.mimic", ["", ".json", ".jsonc"]))

  if mimic_config_file_path == None:
    options["logger"].warn(f"no .mimic(.json)? file has been found: no more work to do. exiting")
    return True

  mimic_config = config.load_mimic_config(mimic_config_file_path)

  if mimic_config == None:
    raise Exception("cloud not apply post clone instruction because of broken mimic config (see https://raw.githubusercontent.com/LasramR/mimic/refs/heads/main/.mimic.schema.json)")
  
  fs.remove_ignore(mimic_config_file_path)

  if mimic_config.git.enabled:
    options["logger"].info(f"initializing new git repository in {mimic_template_dir} with main_branch={mimic_config.git.main_branch}")

  git_action(mimic_template_dir, mimic_config.git)

  options["logger"].info(f"collecting user input(s)")
  variables_values = {}
  for v in mimic_config.template.variables.keys():
    mimic_variable = mimic_config.template.variables[v]
    variables_values[mimic_variable.name] = input.get_user_variable_input(mimic_variable)

  pre_hooks_success = _run_hooks(mimic_template_dir, "pre_template_injection", mimic_config.template.variables, variables_values, mimic_config, options)
  
  if pre_hooks_success:
    options["logger"].info(f"generating mimic_template")
  else:
    options["logger"].warn(f'"pre_template_injection" hooks failed, mimic will still generate your mimic_template but "post_template_injection" hooks will be skipped')

  inject_mimic_template(mimic_template_dir, mimic_config.template.variables, variables_values)

  options["logger"].success(f"{mimic_template_dir} generated")

  if pre_hooks_success:
    if not _run_hooks(mimic_template_dir, "post_template_injection", mimic_config.template.variables, variables_values, mimic_config, options):
      options["logger"].error(f'"post_template_injection" hooks failed')
      return False

  return True