from subprocess import Popen, PIPE
from threading import Thread
from typing import IO, Dict, Any

from .template import inject_variable
from ..utils.config import MimicHookConfig, MimicVariable
from ..utils.input import get_user_confirmation

def _hook_print_command_stream(cp : Popen[str], stream : IO[str]) -> None :
  for x in iter(stream.readline, ''):
    if cp.poll() is not None:
      break
    print(x, end="")

def hook_action(mimic_template_dir : str, hook_config : MimicHookConfig, variables : Dict[str, MimicVariable], variables_values: Dict[str, Any], unsafe_mode : bool = False) -> bool :
  for command in hook_config.steps:
    parsed_command = inject_variable(command, variables, variables_values)
    if unsafe_mode or get_user_confirmation(f"{mimic_template_dir}: `{parsed_command}` will be executed. Continue Y/n ?").upper() == "Y":
      command_cp = Popen([parsed_command], cwd=mimic_template_dir, text=True, shell=True, stdout=PIPE, stderr=PIPE);
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
