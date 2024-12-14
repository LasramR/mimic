from os import sep
from os.path import abspath, exists

from ..options import OrcaOptions
from ..utils import git, fs, config

def clone(options : OrcaOptions) -> bool :
  if options['command']["name"] != "clone":
    raise Exception("clone: invalid options")
  
  repository_url = options["command"]["repository_url"]

  if not git.repository_exists(repository_url):
    raise Exception(f'clone: could not find repository {repository_url}. Are you sure that you have access to the repository ?')

  project_dir = options["command"].get("out_dir") or abspath(git.repository_name(repository_url))

  if exists(project_dir):
    raise Exception(f"clone: out_dir {project_dir} already exist and cloning into it will fail. cancelling")

  options["logger"].info(f"cloning {repository_url} in {project_dir}")
  if not git.clone_repository(repository_url, project_dir):
    raise Exception(f'clone: could not clone repository at "{project_dir}"')
  git.remove_git_folder(project_dir)
  options["logger"].success(f"{repository_url} cloned")
  
  orcarc_file_path = fs.resolve_existing_path(fs.get_file_with_extensions(f"{project_dir}{sep}.orcarc", ["", ".json", ".jsonc"]))

  if orcarc_file_path == None:
    options["logger"].warn(f"no orcarc(.json)? file has been found: no more work to do. exiting")
    return False

  orca_config = config.load_orca_config(orcarc_file_path)

  if orca_config == None:
    raise Exception(f"clone: cloud not apply post clone instruction because of broken orca config (see {orcarc_file_path})")

  return True