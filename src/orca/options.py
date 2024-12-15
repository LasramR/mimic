from os import getcwd
from os.path import abspath, join
from typing import TypedDict, Literal, Union, Any

from .utils.logger import Logger, LoggerOptions

class OrcaCommandOptions (TypedDict):
  name: str

class OrcaCloneOptions (OrcaCommandOptions) :
  name: Literal["clone"]
  repository_url: str
  out_dir: str
  unsafe_mode: bool

def NewOrcaCloneOptions(base_clone_options : OrcaCloneOptions) -> OrcaCloneOptions :
  return {
    "name": "clone",
    "repository_url": base_clone_options["repository_url"],
    "out_dir": abspath(base_clone_options["out_dir"]) if not base_clone_options.get("out_dir") is None else None,
    "unsafe_mode": base_clone_options.get("unsafe_mode", False)
   }

class OrcaLintOptions (OrcaCommandOptions) :
  name: Literal["lint"]
  project_dir: str

def NewOrcaLintOptions(base_lint_options : OrcaLintOptions) -> OrcaLintOptions :
  return {
    "name": "lint",
    "project_dir": abspath(base_lint_options["project_dir"]) if not base_lint_options.get("project_dir") is None else getcwd()
   }

class OrcaAliasAction (TypedDict) :
  name: str

class OrcaAliasAddAction (OrcaAliasAction) :
  name: Literal["add"]
  alias: str
  repository_url: str

class OrcaAliasRmAction (OrcaAliasAction) :
  name: Literal["rm"]
  alias: str

class OrcaAliasListAction (OrcaAliasAction) :
  name: Literal["list"]
  
class OrcaAliasInitAction (OrcaAliasAction) :
  name: Literal["init"]

def NewOrcaAliasAction(name : str, validated_args : Any) -> OrcaAliasAction :
  match name:
    case "add":
      return OrcaAliasAddAction({
        "name": "add",
        "alias": validated_args.alias,
        "repository_url": validated_args.repository_url
      })
    case "rm":
      return OrcaAliasRmAction({
        "name": "rm",
        "alias": validated_args.alias
      })
    case "list":
      return OrcaAliasListAction({
        "name": "list"
      })
    case "init":
      return OrcaAliasInitAction({
        "name": "init"
      })
    case _:
      raise Exception(f"alias: unknown action '{name}'") 


class OrcaAliasOptions (OrcaCommandOptions) :
  name: Literal["alias"]
  action: Union[OrcaAliasAddAction, OrcaAliasRmAction, OrcaAliasListAction, OrcaAliasInitAction]
  orca_config_file_path: Union[str, None]

def NewOrcaAliasOptions(base_alias_options : OrcaAliasOptions) -> OrcaAliasOptions :
  return {
    "name": "alias",
    "action": base_alias_options["action"],
    "orca_config_file_path": abspath(base_alias_options["orca_config_file_path"]) if not base_alias_options.get("orca_config_file_path") is None else abspath(join(__file__, "..", "..", "..", ".aliases"))
  }

class OrcaOptions (TypedDict):
  command: Union[OrcaCloneOptions, OrcaLintOptions, OrcaAliasOptions]
  working_dir: str
  debug: bool
  logger: Logger

def NewOrcaOptions(base_options : OrcaOptions) -> OrcaOptions:
  return {
    "command": base_options["command"],
    "working_dir": getcwd(),
    "debug": base_options.get("debug", False),
    "logger": base_options.get("logger", Logger(LoggerOptions.DefaultWithName("orca")))
  }
