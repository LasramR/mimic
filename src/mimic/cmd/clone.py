from os import sep
from os.path import abspath, exists
from typing import Dict, Any

from ..actions.git import git_action
from ..actions.template import inject_project
from ..actions.hook import hook_action
from ..utils import git, cloning, fs, config, input, alias_wallet
from ..options import MimicOptions

def _run_hooks(project_dir : str, when : config.MimicHookWhenType, variables: Dict[str, Any], mimic_config : config.MimicConfig, options : MimicOptions) -> bool :
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
      hook_result = hook_action(project_dir, h, variables, options["command"]["unsafe_mode"])
    except:
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
  
  alias = options["command"]["repository_uri"]
  repository_uri = alias_wallet.resolve_alias_repository_uri_from(options["command"]["alias_wallet_file_path"], alias)

  if alias != repository_uri:
    options["logger"].info(f"{alias} has been resolved to {repository_uri}")

  options["logger"].info(f"checking access to repository {repository_uri}")
  if not cloning.check_access_to_project(repository_uri):
    raise Exception(f'could not resolve repository {repository_uri}. Are you sure that you have access to the repository ?')

  options["logger"].success(f"ok")

  project_dir = options["command"].get("out_dir") or abspath(git.repository_name(repository_uri))

  if exists(project_dir):
    raise Exception(f"out_dir {project_dir} already exist and cloning into it will fail. cancelling")

  options["logger"].info(f"cloning {repository_uri} in {project_dir}")
  if not cloning.clone_project(repository_uri, project_dir):
    raise Exception(f'could not clone repository at "{project_dir}"')

  options["logger"].success(f"{repository_uri} cloned")


  mimic_config_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{project_dir}{sep}.mimic", ["", ".json", ".jsonc"]))

  if mimic_config_file_path == None:
    options["logger"].warn(f"no .mimic(.json)? file has been found: no more work to do. exiting")
    return True

  mimic_config = config.load_mimic_config(mimic_config_file_path)

  if mimic_config == None:
    raise Exception(f"cloud not apply post clone instruction because of broken mimic config (see {mimic_config_file_path})")
  
  fs.remove_ignore(mimic_config_file_path)

  if mimic_config.git.enabled:
    options["logger"].info(f"initializing new git repository in {project_dir} with main_branch={mimic_config.git.main_branch}")

  git_action(project_dir, mimic_config.git)

  options["logger"].info(f"collecting user input(s)")
  variables = {}
  for v in mimic_config.template.variables.keys():
    variables[mimic_config.template.variables[v].name] = input.get_user_variable_input(mimic_config.template.variables[v])

  pre_hooks_success = _run_hooks(project_dir, "pre_template_injection", variables, mimic_config, options)
  
  if pre_hooks_success:
    options["logger"].info(f"generating project")
  else:
    options["logger"].warn(f'"pre_template_injection" hooks failed, mimic will still generate your project but "post_template_injection" hooks will be skipped')

  inject_project(project_dir, variables)

  options["logger"].success(f"{project_dir} generated")

  if pre_hooks_success:
    if not _run_hooks(project_dir, "post_template_injection", variables, mimic_config, options):
      options["logger"].error(f'"post_template_injection" hooks failed')
      return False

  return True