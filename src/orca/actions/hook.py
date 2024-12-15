from subprocess import Popen, PIPE
from threading import Thread
from typing import IO

from ..utils.config import OrcaHookConfig
from ..utils.input import get_user_confirmation

def _hook_print_command_stream(cp : Popen[str], stream : IO[str]) -> None :
  for x in iter(lambda : stream.readline(1), ''):
    if cp.poll() is not None:
      break
    print(x, end="")

def hook_action(project_dir : str, hook_config : OrcaHookConfig, unsafe_mode : bool = False) -> bool :
  for command in hook_config.steps:
    if unsafe_mode or get_user_confirmation(f"{project_dir}: `{command}` will be executed. Continue Y/n ?").upper() == "Y":
      command_cp = Popen([command], cwd=project_dir, text=True, shell=True, stdout=PIPE, stderr=PIPE);
      stream_threads = [Thread(target=_hook_print_command_stream, args=(command_cp, command_cp.stdout)), Thread(target=_hook_print_command_stream, args=(command_cp, command_cp.stderr))]
      for t in stream_threads:
        t.start()
      for t in stream_threads:
        t.join()
      if command_cp.wait() != 0:
        return False
    else:
      raise Exception("user cancellation")
  return True
