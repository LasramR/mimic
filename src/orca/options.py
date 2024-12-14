from os import getcwd
from os.path import abspath
from typing import TypedDict, Literal, Union

from .utils.logger import Logger, LoggerOptions

class OrcaCommandOptions (TypedDict):
  name: str

class OrcaCloneOptions (OrcaCommandOptions) :
  name: Literal["clone"]
  repository_url: str
  out_dir: str

class OrcaOptions (TypedDict):
  command: Union[OrcaCloneOptions]
  working_dir: str
  debug: bool
  logger: Logger

def NewOrcaCloneOptions(base_clone_options : OrcaCloneOptions) -> OrcaCloneOptions :
  return {
    "name": "clone",
    "repository_url": base_clone_options["repository_url"],
    "out_dir": abspath(base_clone_options["out_dir"]) if not base_clone_options.get("out_dir") is None else None
   }

def NewOrcaOptions(base_options : OrcaOptions) -> OrcaOptions:
  return {
    "command": base_options["command"],
    "working_dir": getcwd(),
    "debug": base_options.get("debug", False),
    "logger": base_options.get("logger", Logger(LoggerOptions.DefaultWithName("orca")))
  }
