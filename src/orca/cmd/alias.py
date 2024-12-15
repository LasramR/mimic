from os.path import exists
from re import match

from ..utils.alias_wallet import Alias, alias_name_regex, alias_wallet_exist, get_alias_wallet_from, save_alias_wallet_to
from ..options import OrcaOptions

def _add_alias(options : OrcaOptions) -> bool :
  alias_wallet_file_path = options["command"]["alias_wallet_file_path"].strip()
  alias_name = options["command"]["action"]["alias"].strip()
  repository_url = options["command"]["action"]["repository_url"].strip()

  if match(alias_name_regex, alias_name) is None:
    raise Exception(f"{alias_name} is an invalid alias. Aliases can contain letters, numbers, underscores and hyphens.")

  if not alias_wallet_exist(alias_wallet_file_path):
    options["logger"].info(f"created alias wallet {alias_wallet_file_path}")
    save_alias_wallet_to(alias_wallet_file_path, None)

  alias_wallet = get_alias_wallet_from(alias_wallet_file_path)

  if alias_name in alias_wallet.aliases:
    raise Exception(f"alias {alias_name} ({alias_wallet.aliases[alias_name].repository_url}) already exist in wallet {alias_wallet_file_path}")
  
  alias_wallet.aliases[alias_name] = Alias(alias_name, repository_url)

  save_alias_wallet_to(alias_wallet_file_path, alias_wallet)

  options["logger"].success(f"saved alias {alias_name} in wallet {alias_wallet_file_path}")
  options["logger"].warn(f"alias wallets are unencrypted, if your alias target contains credentials or an access token, it will be displayed in plain text")

  return True

def _rm_alias(options : OrcaOptions) -> bool :
  alias_wallet_file_path = options["command"]["alias_wallet_file_path"].strip()
  alias_name = options["command"]["action"]["alias"].strip()

  alias_wallet = get_alias_wallet_from(alias_wallet_file_path)

  if not alias_name in alias_wallet.aliases:
    raise Exception(f"wallet {alias_wallet_file_path} does not contain alias {alias_name}")
  
  old_repository_url = alias_wallet.aliases[alias_name].repository_url 
  del alias_wallet.aliases[alias_name]
  
  save_alias_wallet_to(alias_wallet_file_path, alias_wallet)
  options["logger"].success(f"removed alias {alias_name} ({old_repository_url}) from wallet {alias_wallet_file_path}")

  return True

def _list_alias(options : OrcaOptions) -> bool :
  alias_wallet_file_path = options["command"]["alias_wallet_file_path"].strip()

  alias_wallet = get_alias_wallet_from(alias_wallet_file_path)
  alias_count = len(alias_wallet.aliases.keys())
  options["logger"].info(f"wallet {alias_wallet_file_path} ({alias_count} {'entry' if alias_count <= 1 else 'entries'})")
  for alias_name in alias_wallet.aliases.keys():
    print(f"{alias_name} -> {alias_wallet.aliases[alias_name].repository_url}")
  
  return True

def _init_alias(options : OrcaOptions) -> bool :
  alias_wallet_file_path = options["command"]["alias_wallet_file_path"].strip()

  if not alias_wallet_exist(alias_wallet_file_path):
    options["logger"].info(f"created alias wallet {alias_wallet_file_path}")
    save_alias_wallet_to(alias_wallet_file_path, None)
    return True
  
  options["logger"].error(f"wallet {alias_wallet_file_path} already exist")

  return False

def alias(options : OrcaOptions) -> bool :
  if options['command']["name"] != "alias":
    raise Exception("alias: invalid options")
  
  match options["command"]["action"]["name"]:
    case "add":
      return _add_alias(options)
    case "list":
      return _list_alias(options)
    case "rm":
      return _rm_alias(options)
    case "init":
      return _init_alias(options)
    case _ as name:
      raise Exception(f"alias: unknown action '{name}'")