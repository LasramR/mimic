from jsonschema import validate, Draft202012Validator
from json import load
from os.path import join, dirname
from typing import Union, Literal, List, Dict, Any

class MimicGitConfig:
  enabled: bool = False
  main_branch: str = "main"

  def __init__(self, validated_raw : Union[Dict[str, Any], None]):
    if validated_raw == None:
      return
    
    self.enabled = validated_raw.get("enabled", False)
    self.main_branch = validated_raw.get("main_branch", "main")

MimicVariableTypeType = Literal["string", "number", "boolean", "regex", "choice"]

class MimicVariable:
  name: str
  type: MimicVariableTypeType
  required: bool = True
  description: Union[str, None] = None
  item: Union[Any, None] = None
  default: Any

  def __init__(self, name: str, validated_raw : Dict[str, Any]):
    self.name = name
    self.type = validated_raw["type"]
    self.required = validated_raw.get("required", True)
    self.description = validated_raw.get("description", None)
    
    if self.type == "regex":
      self.item = rf"{validated_raw.get('item', None)}"
    else:
      self.item = validated_raw.get("item", None)

    if self.type == "boolean":
      self.default = validated_raw.get("default", False)
    else:
      self.default = validated_raw.get("default", None)

  def format_variable_value(self, value : Any):
    if self.type == "boolean":
      if self.item != "Capitalized":
        return str(value).lower()
    return str(value)

  @staticmethod
  def NewFrom(name : str, type : MimicVariableTypeType, required: bool = True, description: Union[str, None] = None, item: Union[Any, None] = None, default : Any = None):
    if type == "regex" and not isinstance(item, str):
      raise Exception("could not create MimicVariable of type regex without a valid item (str) qualifier")
    
    if type == "choice" and (not isinstance(item, list) or len(item) < 1 or not isinstance(item[0], str)):
      raise Exception("could not create MimicVariable of type regex without a valid item (List[str]) qualifier")

    return MimicVariable(name, {
      "type": type,
      "required": required,
      "description": description,
      "item": item,
      "default": default
    })
  
class MimicFileContentPreview:

  raw : str
  parsed: str
  line: int

  def __init__(self, raw : str, parsed: str, line: int):
    self.raw = raw
    self.parsed = parsed
    self.line = line

class MimicPreview:

  directory_preview: Dict[str, str]
  file_preview: Dict[str, str]
  file_content_preview: Dict[str, List[MimicFileContentPreview]]

  def __init__(self):
    self.directory_preview = {}
    self.file_preview = {}
    self.file_content_preview = {}

class MimicTemplateConfig:
  ignorePatterns: List[str]
  variables: Dict[str, MimicVariable]

  def __init__(self, validated_raw : Union[Dict[str, Any], None]):
    if validated_raw == None:
      return
    
    self.ignorePatterns = validated_raw.get("ignorePatterns", [])

    self.variables = {}
    if raw_variables := validated_raw.get("variables"):
      for v in raw_variables.keys():
        self.variables[v] = MimicVariable(v, raw_variables[v])

MimicHookWhenType = Literal["pre_template_injection", "post_template_injection"]

class MimicHookConfig:
  name: Union[str, None]
  when: MimicHookWhenType
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

class MimicConfig:
  git: MimicGitConfig
  template: MimicTemplateConfig
  hooks: List[MimicHookConfig] = []

  def __init__(self, validated_raw : Dict[str, Any]):
    self.git = MimicGitConfig(validated_raw.get("git", None))
    self.template = MimicTemplateConfig(validated_raw.get("template", None))
    if raw_hooks := validated_raw.get("hooks"):
      for h in raw_hooks:
        self.hooks.append(MimicHookConfig(h))

  def get_hooks_when(self, when : MimicHookWhenType) -> List[MimicHookConfig]:
    return list(filter(lambda h: h.when == when, self.hooks))

class MimicConfigIssue:
  property: str
  reason: str

  def __init__(self, property : str, reason : str):
    self.property = property
    self.reason = reason

def is_mimic_config_file_data_valid(mimic_config_file_path : str) -> List[MimicConfigIssue]:
  with open(join(dirname(__file__), "..", "..", "..", ".mimic.schema.json"), "r") as fd:
    schema = load(fd)

  with open(mimic_config_file_path, "r") as fd:
    mimic_config_file_data = load(fd)

    validator = Draft202012Validator(schema)
    validator_errors = sorted(validator.iter_errors(mimic_config_file_data), key=lambda e: e.path)
    format_issues = []

    for error in validator_errors:
      format_issues.append(MimicConfigIssue('.'.join(map(str, error.path)), error.message))

    return format_issues

def load_mimic_config(mimic_config_file_path : str) -> Union[MimicConfig, None]:
  try:
    with open(join(dirname(__file__), "..", "..", "..", ".mimic.schema.json"), "r") as fd:
      schema = load(fd)

    with open(mimic_config_file_path, "r") as fd:
      mimic_config_file_data = load(fd)
      validate(mimic_config_file_data, schema)
      return MimicConfig(mimic_config_file_data)
  except Exception as e:
    return None
