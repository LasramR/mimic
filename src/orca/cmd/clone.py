from os import sep
from os.path import abspath, exists

from ..actions.git import git_action
from ..actions.template import inject_project
from ..actions.hook import hook_action
from ..utils import git, fs, config, input
from ..options import OrcaOptions

def clone(options : OrcaOptions) -> bool :
  if options['command']["name"] != "clone":
    raise Exception("clone: invalid options")
  
  repository_url = options["command"]["repository_url"]

  options["logger"].info(f"resolving repository {repository_url}")
  if not git.repository_exists(repository_url):
    raise Exception(f'could not resolve repository {repository_url}. Are you sure that you have access to the repository ?')

  project_dir = options["command"].get("out_dir") or abspath(git.repository_name(repository_url))

  if exists(project_dir):
    raise Exception(f"out_dir {project_dir} already exist and cloning into it will fail. cancelling")

  options["logger"].info(f"cloning {repository_url} in {project_dir}")
  if not git.clone_repository(repository_url, project_dir):
    raise Exception(f'could not clone repository at "{project_dir}"')
  git.remove_git_folder(project_dir)
  options["logger"].success(f"{repository_url} cloned")
  
  orcarc_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{project_dir}{sep}.orcarc", ["", ".json", ".jsonc"]))

  if orcarc_file_path == None:
    options["logger"].warn(f"no orcarc(.json)? file has been found: no more work to do. exiting")
    return True

  orca_config = config.load_orca_config(orcarc_file_path)
  fs.remove_ignore(orcarc_file_path)

  if orca_config == None:
    raise Exception(f"cloud not apply post clone instruction because of broken orca config (see {orcarc_file_path})")
  
  if orca_config.git.enabled:
    options["logger"].info("configuring git")
  git_action(project_dir, orca_config.git)

  pre_template_injection_hooks = orca_config.get_pre_template_injection_hooks()
  options["logger"].info(f"running 'pre_template_injection' hooks ({len(pre_template_injection_hooks)})")
  for h in pre_template_injection_hooks:
    options["logger"].info(f"hook: '{h.name}'")
    hook_action(project_dir, h, options["command"]["unsafe_mode"])

  variables = {}
  for v in orca_config.template.variables.keys():
    variables[orca_config.template.variables[v].name] = input.get_user_variable_input(orca_config.template.variables[v])

  options["logger"].info(f"generating injected project {project_dir}")
  inject_project(project_dir, variables)

  post_template_injection_hooks = orca_config.get_post_template_injection_hooks()
  options["logger"].info(f"running 'post_template_injection' hooks ({len(post_template_injection_hooks)})")
  for h in post_template_injection_hooks:
    options["logger"].info(f"hook: '{h.name or '<unnamed hook>'}'")
    hook_action(project_dir, h, options["command"]["unsafe_mode"])
  return True