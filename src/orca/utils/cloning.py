from os.path import exists
from shutil import copytree

from . import git

def check_access_to_project(repository_uri : str) -> bool :
  if exists(repository_uri):
    return True
  return git.repository_exists(repository_uri)

def clone_project(repository_uri : str, project_dir : str) -> bool :
  if exists(repository_uri):
    try:
      return copytree(repository_uri, project_dir, dirs_exist_ok=False)
    except:
      return False
  
  if git.clone_repository(repository_uri, project_dir):
    git.remove_git_folder(project_dir)
    return True
  
  return False