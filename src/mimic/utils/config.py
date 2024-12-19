from jsonschema import validate, Draft202012Validator
from json import load, dump
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
  
  def toJSON(self) -> Dict[str, Any] :
    jsoned = {}

    jsoned["enabled"] = self.enabled
    jsoned["main_branch"] = self.main_branch

    return jsoned

MimicVariableTypeType = Literal["string", "number", "boolean", "regex", "choice"]

class MimicVariable:
  name: str
  type: MimicVariableTypeType
  required: bool = True
  description: Union[str, None] = None
  item: Union[Any, None] = None
  default: Union[Any, None] = None

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
  
  def toJSON(self) -> Dict[str, Any]:
    jsoned = {}

    jsoned["type"] = self.type
    jsoned["required"] = self.required
    
    if self.description != None:
      jsoned["description"] = self.description
    
    if self.item != None:
      jsoned["item"] = self.item

    if self.default != None:
      jsoned["default"] = self.default

    return jsoned

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

  def toJSON(self) -> Dict[str, Any]:
    jsoned = {}
    
    jsoned["ignorePatterns"] = self.ignorePatterns
    
    jsoned["variables"] = {}
    for v in self.variables.keys():
      jsoned["variables"][v] = self.variables[v].toJSON()

    return jsoned

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
  
  def toJSON(self) -> Dict[str, Any]:
    jsoned = {}

    if self.name != None:
      jsoned["name"] = self.name

    jsoned["when"] = self.when
    jsoned["steps"] = self.steps
    jsoned["ignore_error"] = self.ignore_error
    jsoned["ignore_user_skip"] = self.ignore_user_skip

    return jsoned

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

  def toJSON(self) -> Dict[str, Any]:
    return {
      "$schema": "https://raw.githubusercontent.com/LasramR/mimic/refs/heads/main/.mimic.schema.json",
      "git": self.git.toJSON(),
      "template": self.template.toJSON(),
      "hooks": [
        h.toJSON() for h in self.hooks
      ]
    }

class MimicConfigIssue:
  property: str
  reason: str

  def __init__(self, property : str, reason : str):
    self.property = property
    self.reason = reason

def is_mimic_config_file_data_valid(mimic_config_file_path : str) -> List[MimicConfigIssue]:
  with open(join(dirname(__file__), "..", "..", "..", ".mimic.schema.json"), "r") as fd:
    schema = load(fd)

  try:
    with open(mimic_config_file_path, "r") as fd:
      mimic_config_file_data = load(fd)

      validator = Draft202012Validator(schema)
      validator_errors = sorted(validator.iter_errors(mimic_config_file_data), key=lambda e: e.path)
      format_issues = []

      for error in validator_errors:
        format_issues.append(MimicConfigIssue('.'.join(map(str, error.path)), error.message))

      return format_issues
  except Exception as e:
    return [MimicConfigIssue(mimic_config_file_path, e)]

def load_mimic_config(mimic_config_file_path : str) -> Union[MimicConfig, None]:
  try:
    with open(join(dirname(__file__), "..", "..", "..", ".mimic.schema.json"), "r") as fd:
      schema = load(fd)

    with open(mimic_config_file_path, "r") as fd:
      mimic_config_file_data = load(fd)
      validate(mimic_config_file_data, schema)
      return MimicConfig(mimic_config_file_data)
  except Exception:
    return None

def overwrite_mimic_config(mimic_config_file_path : str, mimic_config : MimicConfig) -> bool:
  try:
    with open(mimic_config_file_path, "w") as fd:
      dump(mimic_config.toJSON(), fd, indent=2)
      return True
  except:
    return False

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