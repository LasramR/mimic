from jsonschema import validate, Draft202012Validator
from json import load
from os import remove
from typing import Union, Literal, List, Dict, Any

class OrcaGitConfig:
  enabled: bool = False
  main_branch: str = "main"

  def __init__(self, validated_raw : Union[Dict[str, Any], None]):
    if validated_raw == None:
      return
    
    self.enabled = validated_raw.get("enabled", False)
    self.main_branch = validated_raw.get("main_branch", "main")

OrcaVariableTypeType = Literal["string", "number", "boolean", "regex", "choice"]

class OrcaVariable:
  name: str
  type: OrcaVariableTypeType
  required: bool = True
  description: Union[str, None] = None
  item: Union[Any, None] = None

  def __init__(self, name: str, validated_raw : Dict[str, Any]):
    self.name = name
    self.type = validated_raw["type"]
    self.required = validated_raw.get("required", True)
    self.description = validated_raw.get("description", None)
    if self.type == "regex":
      self.item = rf"{validated_raw.get('item', None)}"
    else:
      self.item = validated_raw.get("item", None)

  @staticmethod
  def NewFrom(name : str, type : OrcaVariableTypeType, required: bool = True, description: Union[str, None] = None, item: Union[Any, None] = None):
    if type == "regex" and not isinstance(item, str):
      raise Exception("could not create OrcaVariable of type regex without a valid item (str) qualifier")
    
    if type == "choice" and (not isinstance(item, list) or len(item) < 1 or not isinstance(item[0], str)):
      raise Exception("could not create OrcaVariable of type regex without a valid item (List[str]) qualifier")

    return OrcaVariable(name, {
      "type": type,
      "required": required,
      "description": description,
      "item": item
    })
  
class OrcaVariableReference:

  def __init__(self, name: str, source_path: str, is_directory : bool = False, is_file = False):
    self.name = name
    self.source_path = source_path
    self.is_directory = is_directory
    self.is_file = is_file

class OrcaTemplateConfig:
  variables: Dict[str, OrcaVariable] = {}

  def __init__(self, validated_raw : Union[Dict[str, Any], None]):
    if validated_raw == None:
      return
    
    if raw_variables := validated_raw.get("variables"):
      for v in raw_variables.keys():
        self.variables[v] = OrcaVariable(v, raw_variables[v])

OrcaHookWhenType = Literal["pre_template_injection", "post_template_injection"]

class OrcaHookConfig:
  name: Union[str, None]
  when: OrcaHookWhenType
  steps: List[str] = []
  ignore_error: bool
  ignore_user_skip: bool

  def __init__(self, validated_raw : Union[Dict[str, Any], None]):
    if validated_raw == None:
      return
    
    self.name = validated_raw.get("name")
    self.when = validated_raw["when"]
    self.steps = validated_raw["steps"]
    self.ignore_error = validated_raw.get("ignore_error", False)
    self.ignore_user_skip = validated_raw.get("ignore_user_skip", False)

class OrcaConfig:
  git: OrcaGitConfig
  template: OrcaTemplateConfig
  hooks: List[OrcaHookConfig] = []

  def __init__(self, validated_raw : Dict[str, Any]):
    self.git = OrcaGitConfig(validated_raw.get("git", None))
    self.template = OrcaTemplateConfig(validated_raw.get("template", None))
    if raw_hooks := validated_raw.get("hooks"):
      for h in raw_hooks:
        self.hooks.append(OrcaHookConfig(h))

  def get_hooks_when(self, when : OrcaHookWhenType) -> List[OrcaHookConfig]:
    return list(filter(lambda h: h.when == when, self.hooks))

class OrcaConfigIssue:
  property: str
  reason: str

  def __init__(self, property : str, reason : str):
    self.property = property
    self.reason = reason

def is_orcarc_data_valid(orcarc_file_path : str) -> List[OrcaConfigIssue]:
  with open("orcarc.schema.json", "r") as fd:
    schema = load(fd)

  with open(orcarc_file_path, "r") as fd:
    orcarc_data = load(fd)

    validator = Draft202012Validator(schema)
    validator_errors = sorted(validator.iter_errors(orcarc_data), key=lambda e: e.path)
    format_issues = []

    for error in validator_errors:
      format_issues.append(OrcaConfigIssue('.'.join(map(str, error.path)), error.message))

    return format_issues

def load_orca_config(orcarc_file_path : str) -> Union[OrcaConfig, None]:
  try:
    with open("orcarc.schema.json", "r") as fd:
      schema = load(fd)

    with open(orcarc_file_path, "r") as fd:
      orcarc_data = load(fd)
      validate(orcarc_data, schema)
      return OrcaConfig(orcarc_data)
  except Exception as e:
    return None
