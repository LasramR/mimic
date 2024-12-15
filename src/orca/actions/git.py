from ..utils import git, config, input

def git_action(project_dir : str, git_config : config.OrcaGitConfig) -> bool :
  git.remove_git_folder(project_dir) # Ensure this is gone

  if not git_config.enabled:
    return True

  remote_uri = input.get_user_str_input("remote origin", required=False)

  return git.init_new_repository(project_dir, git_config.main_branch, remote_uri)
