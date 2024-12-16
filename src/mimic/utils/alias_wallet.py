from os import linesep
from os.path import exists
from re import match
from typing import List, Dict, Union

class Alias:

  def __init__(self, name : str, mimic_uri : str):
    self.name = name
    self.mimic_uri = mimic_uri

alias_name_regex = r"^[a-zA-Z_-]+$"
alias_regex = r"^\s*(?P<name>[a-zA-Z_-]+)\s+(?P<mimic_uri>[^\s]+)\s*$"

class AliasWallet:

  aliases : Dict[str, Alias]

  def __init__(self, raw_aliases : List[str]):
    self.aliases = {}
    for raw_alias in raw_aliases:
      groups = match(alias_regex, raw_alias)

      if groups == None:
        continue

      name, mimic_uri = groups.group("name"), groups.group("mimic_uri")

      if name == None or mimic_uri == None:
        continue

      self.aliases[name] = Alias(name, mimic_uri)

def alias_wallet_exist(alias_wallet_file_path : str) -> bool :
  return exists(alias_wallet_file_path)

def save_alias_wallet_to(alias_wallet_file_path : str, alias_wallet : Union[AliasWallet, None]) -> bool :
  try:
    with open(alias_wallet_file_path, "w") as fd:
      if alias_wallet == None:
        fd.write("")
        return True
      
      for alias_name in alias_wallet.aliases.keys():
        fd.write(f"{alias_wallet.aliases[alias_name].name} {alias_wallet.aliases[alias_name].mimic_uri}{linesep}")
      
      return True
  except:
    return False

def get_alias_wallet_from(alias_wallet_file_path : str) -> AliasWallet :
  if not alias_wallet_exist(alias_wallet_file_path):
    raise Exception(f"cannot find wallet {alias_wallet_file_path}")
  
  with open(alias_wallet_file_path, "r") as fd:
    return AliasWallet(fd.readlines())

def resolve_alias_mimic_uri_from(alias_wallet_file_path : str, alias_name : str) -> str :
  """
  If no matching alias is found, return alias as the mimic uri
  """

  if not alias_wallet_exist(alias_wallet_file_path):
    return alias_name
  
  alias_wallet = get_alias_wallet_from(alias_wallet_file_path)

  if not alias_name in alias_wallet.aliases:
    return alias_name
  
  return alias_wallet.aliases[alias_name].mimic_uri
