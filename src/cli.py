from argparse import ArgumentParser
from signal import SIGINT, signal

from mimic.cmd.alias import alias
from mimic.cmd.clone import clone
from mimic.cmd.lint import lint
from mimic.cmd.init import init
from mimic.cmd.preview import preview
from mimic.options import NewMimicCloneOptions, NewMimicInitOptions, NewMimicLintOptions, NewMimicOptions, NewMimicAliasOptions, NewMimicAliasAction, NewMimicPreviewOptions

def main():
  signal(SIGINT, lambda _a, _b: print() or exit(-1))
  arg_parser = ArgumentParser(prog="mimic")

  sub_parser = arg_parser.add_subparsers(dest="command", required=True)
  
  clone_parser = sub_parser.add_parser("clone", description="clone and generate a mimic from a mimic template")
  clone_parser.add_argument("mimic_uri", type=str, help="URI to a mimic template (either a git repository or a path to a local mimic template)")
  clone_parser.add_argument("out_dir", type=str, help="mimic output directory", nargs='?')
  clone_parser.add_argument("-u", "--unsafe", action="store_true", help="enable unsafe mode, hooks will run without user confirmation")
  clone_parser.add_argument("-f", "--file", help="mimic wallet to use to resolve alias")


  lint_parser = sub_parser.add_parser("lint", description="detect errors in your mimic template")
  lint_parser.add_argument("mimic_template_dir", type=str, help="mimic template directory", nargs='?')
  lint_parser.add_argument("--fix", action="store_true", help="automatically fix mimic template issues")

  alias_parser = sub_parser.add_parser("alias", description="manage your aliases: shortnames pointing to mimic templates")
  alias_action_sub_parser = alias_parser.add_subparsers(dest="action", required=True)

  alias_add_parser = alias_action_sub_parser.add_parser("add", description="add a new alias in your mimic wallet")
  alias_add_parser.add_argument("alias", type=str, help="alias to add")
  alias_add_parser.add_argument("mimic_uri", type=str, help="URI to a mimic template")
  alias_add_parser.add_argument("-f", "--file", help="mimic wallet to use")

  alias_rm_parser = alias_action_sub_parser.add_parser("rm", description="remove an alias from your mimic wallet")
  alias_rm_parser.add_argument("alias", type=str, help="alias to remove")
  alias_rm_parser.add_argument("-f", "--file", help="wallet file to use")

  alias_list_parser = alias_action_sub_parser.add_parser("list", description="list aliases from your mimic wallet")
  alias_list_parser.add_argument("-f", "--file", help="specifies which mimic wallet to use")
  
  alias_init_parser = alias_action_sub_parser.add_parser("init", description="create a new mimic wallet")
  alias_init_parser.add_argument("file", help="specifies where to create a new mimic wallet, defaults to ~/.mimic/wallet.mimic", nargs='?')

  init_parser = sub_parser.add_parser("init", description="setup a new mimic template")
  init_parser.add_argument("mimic_template_dir", type=str, help="mimic template directory", nargs='?')

  preview_parser = sub_parser.add_parser("preview", description="Preview your mimic template")
  preview_parser.add_argument("mimic_template_dir", type=str, help="mimic template directory", nargs='?')

  args = arg_parser.parse_args()

  command_options = None
  match args.command:
    case "clone":
      command_options = NewMimicCloneOptions({
        "out_dir": args.out_dir,
        "mimic_uri": args.mimic_uri,
        "unsafe_mode": args.unsafe,
        "alias_wallet_file_path": args.file
      })
    case "lint":
      command_options = NewMimicLintOptions({
        "mimic_template_dir": args.mimic_template_dir,
        "fix": args.fix
      })
    case "alias": 
      command_options = NewMimicAliasOptions({
      "action": NewMimicAliasAction(args.action, args),
      "alias_wallet_file_path": args.file
    })
    case "init":
      command_options = NewMimicInitOptions({
        "mimic_template_dir": args.mimic_template_dir
      })
    case "preview":
      command_options = NewMimicPreviewOptions({
        "mimic_template_dir": args.mimic_template_dir
      })
    case _ as unknown:
      arg_parser.error(f'unknown command "{unknown}". Use -h,--help for usage information.')

  options = NewMimicOptions({
    "command": command_options,
  })

  result = False
  try:
    match options["command"]["name"]:
      case "alias":
        result = alias(options)
      case "clone":
        result = clone(options)
      case "lint":
        result = lint(options)
      case "init":
        result = init(options)
      case "preview":
        result = preview(options)
      case _ as unknown:
        options["logger"].error(f'unknown command "{unknown}". Use -h,--help for usage information.')
  except Exception as e:
    options["logger"].error(e)

  exit(0 if result else 1)

if __name__ == "__main__":
  main()
