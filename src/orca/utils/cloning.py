from os.path import exists
from shutil import copytree

from . import git

def check_access_to_project(repository_url : str) -> bool :
  if exists(repository_url):
    return True
  return git.repository_exists(repository_url)

def clone_project(repository_url : str, project_dir : str) -> bool :
  if exists(repository_url):
    try:
      return copytree(repository_url, project_dir, dirs_exist_ok=False)
    except:
      return False
  
  if git.clone_repository(repository_url, project_dir):
    git.remove_git_folder(project_dir)
    return True
  
  return False