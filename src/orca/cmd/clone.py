from os import sep
from os.path import abspath, exists

from ..actions.git import git_action
from ..actions.template import inject_project
from ..actions.hook import hook_action
from ..utils import git, cloning, fs, config, input, alias_wallet
from ..options import OrcaOptions

def _run_hooks(project_dir : str, when : config.OrcaHookWhenType, orca_config : config.OrcaConfig, options : OrcaOptions) -> None :
  hooks = orca_config.get_hooks_when(when)
  options["logger"].info(f"running '{when}' hooks ({len(hooks)})")
  for h in hooks:
    options["logger"].info(f"hook '{h.name or '<unnamed hook>'}'")

    hook_result = False
    try:
      hook_result = hook_action(project_dir, h, options["command"]["unsafe_mode"])
    except Exception as e:
      if h.ignore_user_skip:
        options["logger"].warn(f"hook '{h.name or '<unnamed hook>'}' skipped")
      else:
        raise e

    if not hook_result:
      if h.ignore_error:
        options["logger"].warn(f"hook '{h.name or '<unnamed hook>'}' failed but non fatal")
      else:
        raise Exception(f"hook '{h.name or '<unnamed hook>'}' failed")

def clone(options : OrcaOptions) -> bool :
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


  orcarc_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{project_dir}{sep}.orcarc", ["", ".json", ".jsonc"]))

  if orcarc_file_path == None:
    options["logger"].warn(f"no orcarc(.json)? file has been found: no more work to do. exiting")
    return True

  orca_config = config.load_orca_config(orcarc_file_path)
  fs.remove_ignore(orcarc_file_path)

  if orca_config == None:
    raise Exception(f"cloud not apply post clone instruction because of broken orca config (see {orcarc_file_path})")
  
  if orca_config.git.enabled:
    options["logger"].info(f"initializing new git repository in {project_dir} with main_branch={orca_config.git.main_branch}")

  git_action(project_dir, orca_config.git)

  if not _run_hooks(project_dir, "pre_template_injection", orca_config, options):
    pass

  options["logger"].info(f"generating project {project_dir}")
  variables = {}
  for v in orca_config.template.variables.keys():
    variables[orca_config.template.variables[v].name] = input.get_user_variable_input(orca_config.template.variables[v])
  
  inject_project(project_dir, variables)

  options["logger"].success("ok")

  if not _run_hooks(project_dir, "post_template_injection", orca_config, options):
    pass

  return True