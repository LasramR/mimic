from shutil import rmtree
from os import sep
from os.path import basename
from subprocess import run, PIPE
from typing import Union  

def repository_exists(repository_uri : str) -> bool :
  return run(
    ["git", "ls-remote", repository_uri],
    env={"GIT_ASKPASS": "echo"},
    stdout=PIPE,
    stderr=PIPE
  ).returncode == 0

def repository_name(repository_uri : str) -> bool :
  return basename(repository_uri).removesuffix(".git")  

def clone_repository(repository_uri : str, out_dir : str) -> bool :
  return run(
    ["git", "clone", repository_uri, out_dir],
    env={"GIT_ASKPASS": "echo"},
    stdout=PIPE,
    stderr=PIPE
  ).returncode == 0

def remove_git_folder(mimic_template_dir : str) :
  rmtree(f"{mimic_template_dir}{sep}.git/", ignore_errors=True)

def init_new_repository(mimic_template_dir : str, main_branch : str, remote_uri : Union[str, None]) -> bool :
  init_cp = run(
    ["git", "init", "-b", main_branch],
    cwd=mimic_template_dir,
    stdout=PIPE,
    stderr=PIPE
  )

  if init_cp.returncode != 0:
    return False
  
  if remote_uri == None:
    return True
  
  add_remote_cp = run(
    ["git", "remote", "add", "origin", remote_uri],
    cwd=mimic_template_dir,
    stdout=PIPE,
    stderr=PIPE
  )

  return add_remote_cp.returncode != 0