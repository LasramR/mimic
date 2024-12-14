from shutil import rmtree
from os import sep
from os.path import basename
from subprocess import run, PIPE
from typing import Union  

def repository_exists(repository_url : str) -> bool :
  return run(
    ["git", "ls-remote", repository_url],
    env={"GIT_ASKPASS": "echo"},
    stdout=PIPE,
    stderr=PIPE
  ).returncode == 0

def repository_name(repository_url : str) -> bool :
  return basename(repository_url).removesuffix(".git")  

def clone_repository(repository_url : str, out_dir : str) -> bool :
  return run(
    ["git", "clone", repository_url, out_dir],
    env={"GIT_ASKPASS": "echo"},
    stdout=PIPE,
    stderr=PIPE
  ).returncode == 0

def remove_git_folder(project_dir : str) :
  rmtree(f"{project_dir}{sep}.git/", ignore_errors=True)

def init_new_repository(project_dir : str, main_branch : str, remote_url : Union[str, None]) -> bool :
  init_cp = run(
    ["git", "init", "-b", main_branch],
    cwd=project_dir,
    stdout=PIPE,
    stderr=PIPE
  )

  if init_cp.returncode != 0:
    return False
  
  if remote_url == None:
    return True
  
  add_remote_cp = run(
    ["git", "remote", "add", "origin", remote_url],
    cwd=project_dir,
    stdout=PIPE,
    stderr=PIPE
  )

  return add_remote_cp.returncode != 0