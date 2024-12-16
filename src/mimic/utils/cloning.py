from os.path import exists
from shutil import copytree

from . import git

def check_access_to_mimic_template(mimic_uri : str) -> bool :
  if exists(mimic_uri):
    return True
  return git.repository_exists(mimic_uri)

def clone_mimic_template(mimic_uri : str, mimic_template_dir : str) -> bool :
  if exists(mimic_uri):
    try:
      return copytree(mimic_uri, mimic_template_dir, dirs_exist_ok=False)
    except:
      return False
  
  if git.clone_repository(mimic_uri, mimic_template_dir):
    git.remove_git_folder(mimic_template_dir)
    return True
  
  return False