from os import getcwd
from os.path import abspath, join, dirname, exists
from typing import TypedDict, Literal, Union, Any

from .utils.logger import Logger, LoggerOptions

class MimicCommandOptions (TypedDict):
  name: str

class MimicCloneOptions (MimicCommandOptions) :
  name: Literal["clone"]
  mimic_uri: str
  out_dir: str
  unsafe_mode: bool
  alias_wallet_file_path: str

def NewMimicCloneOptions(base_clone_options : MimicCloneOptions) -> MimicCloneOptions :
  return {
    "name": "clone",
    "mimic_uri": base_clone_options["mimic_uri"],
    "out_dir": abspath(base_clone_options["out_dir"]) if not base_clone_options.get("out_dir") is None else None,
    "unsafe_mode": base_clone_options.get("unsafe_mode", False),
    "alias_wallet_file_path": abspath(base_clone_options["alias_wallet_file_path"]) if not base_clone_options.get("alias_wallet_file_path") is None else abspath(join(dirname(__file__), "..", "..", "wallet.mimic"))

   }

class MimicLintOptions (MimicCommandOptions) :
  name: Literal["lint"]
  project_dir: str

def NewMimicLintOptions(base_lint_options : MimicLintOptions) -> MimicLintOptions :
  return {
    "name": "lint",
    "project_dir": abspath(base_lint_options["project_dir"]) if not base_lint_options.get("project_dir") is None else getcwd()
   }

class MimicAliasAction (TypedDict) :
  name: str

class MimicAliasAddAction (MimicAliasAction) :
  name: Literal["add"]
  alias: str
  mimic_uri: str

class MimicAliasRmAction (MimicAliasAction) :
  name: Literal["rm"]
  alias: str

class MimicAliasListAction (MimicAliasAction) :
  name: Literal["list"]
  
class MimicAliasInitAction (MimicAliasAction) :
  name: Literal["init"]

def NewMimicAliasAction(name : str, validated_args : Any) -> MimicAliasAction :
  match name:
    case "add":
      return MimicAliasAddAction({
        "name": "add",
        "alias": validated_args.alias,
        "mimic_uri": abspath(validated_args.mimic_uri) if exists(validated_args.mimic_uri) else validated_args.mimic_uri
      })
    case "rm":
      return MimicAliasRmAction({
        "name": "rm",
        "alias": validated_args.alias
      })
    case "list":
      return MimicAliasListAction({
        "name": "list"
      })
    case "init":
      return MimicAliasInitAction({
        "name": "init"
      })
    case _:
      raise Exception(f"alias: unknown action '{name}'") 


class MimicAliasOptions (MimicCommandOptions) :
  name: Literal["alias"]
  action: Union[MimicAliasAddAction, MimicAliasRmAction, MimicAliasListAction, MimicAliasInitAction]
  alias_wallet_file_path: Union[str, None]

def NewMimicAliasOptions(base_alias_options : MimicAliasOptions) -> MimicAliasOptions :
  return {
    "name": "alias",
    "action": base_alias_options["action"],
    "alias_wallet_file_path": abspath(base_alias_options["alias_wallet_file_path"]) if not base_alias_options.get("alias_wallet_file_path") is None else abspath(join(dirname(__file__), "..", "..", "wallet.mimic"))
  }

class MimicInitOptions (MimicCommandOptions):
  name: Literal["init"]
  project_dir: str

def NewMimicInitOptions(base_init_options : MimicInitOptions) -> MimicInitOptions :
  return {
    "name": "init",
    "project_dir": abspath(base_init_options["project_dir"]) if not base_init_options.get("project_dir") is None else getcwd()
   }

class MimicPreviewOptions (MimicCommandOptions):
  name: Literal["preview"]
  project_dir : str

def NewMimicPreviewOptions(base_preview_options : MimicPreviewOptions) -> MimicPreviewOptions :
  return {
    "name": "preview",
    "project_dir": abspath(base_preview_options["project_dir"]) if not base_preview_options.get("project_dir") is None else getcwd()
   }

class MimicOptions (TypedDict):
  command: Union[MimicCloneOptions, MimicLintOptions, MimicAliasOptions, MimicInitOptions, MimicPreviewOptions]
  working_dir: str
  logger: Logger

def NewMimicOptions(base_options : MimicOptions) -> MimicOptions:
  return {
    "command": base_options["command"],
    "working_dir": getcwd(),
    "logger": base_options.get("logger", Logger(LoggerOptions.DefaultWithName("mimic")))
  }
