from jsonschema import ValidationError, validate, Draft202012Validator
from json import load
from typing import TypedDict, Union, Literal, List, Dict, Any

class OrcaGitConfig:
  enabled: bool = False
  main_branch: str = "main"

  def __init__(self, validated_raw : Union[Dict[str, Any], None]):
    if validated_raw == None:
      return
    
    self.enabled = validated_raw.get("enabled", False)
    self.main_branch = validated_raw.get("main_branch", "main")

class OrcaPostInstallConfig:
  steps: List[str] = []

  def __init__(self, validated_raw : Union[Dict[str, Any], None]):
    if validated_raw == None:
      return
    
    self.steps = validated_raw["steps"]

class OrcaVariable:
  name: str
  type: Literal["string", "number", "boolean"]
  required: bool = False
  description: Union[str, None] = None

  def __init__(self, name: str, validated_raw : Dict[str, Any]):
    self.name = name
    self.type = validated_raw["type"]
    self.required = validated_raw.get("required", False)
    self.description = validated_raw.get("description", None)

class OrcaTemplateConfig:
  variables: Dict[str, OrcaVariable] = {}

  def __init__(self, validated_raw : Union[Dict[str, Any], None]):
    if validated_raw == None:
      return
    
    if raw_variables := validated_raw.get("variables"):
      for v in raw_variables.keys():
        self.variables[v] = OrcaVariable(v, raw_variables[v])

class OrcaConfig:
  git: OrcaGitConfig
  template: OrcaTemplateConfig
  post_install: OrcaPostInstallConfig

  def __init__(self, validated_raw : Dict[str, Any]):
    self.git = OrcaGitConfig(validated_raw.get("git", None))
    self.template = OrcaTemplateConfig(validated_raw.get("template", None))
    self.post_install = OrcaPostInstallConfig(validated_raw.get("post_install", None))

class OrcaConfigIssue:
  property: str
  reason: str

  def __init__(self, property : str, reason : str):
    self.property = property
    self.reason = reason

def is_orcarc_data_valid(orcarc_file_path : str) -> List[str]:
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
  except:
    return None
