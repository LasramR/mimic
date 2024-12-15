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

  arg_parser.add_argument("-d", "--debug", action='store_true', help="Enable debug mode\ndisabled by default", required=False)

  sub_parser = arg_parser.add_subparsers(dest="command", required=True)
  
  clone_parser = sub_parser.add_parser("clone", description="clone repository")
  clone_parser.add_argument("repository_uri", type=str, help="URI of the repository to clone")
  clone_parser.add_argument("out_dir", type=str, help="Specify the output directory", nargs='?')
  clone_parser.add_argument("-u", "--unsafe", action="store_true", help="Enable unsafe mode, hooks will run without user confirmation")
  clone_parser.add_argument("-f", "--file", help="Specify mimic wallet file to use")


  lint_parser = sub_parser.add_parser("lint", description="lint mimic template")
  lint_parser.add_argument("project_dir", type=str, help="Specify the mimic project directory", nargs='?')

  alias_parser = sub_parser.add_parser("alias", description="alias")
  alias_action_sub_parser = alias_parser.add_subparsers(dest="action", required=True)

  alias_add_parser = alias_action_sub_parser.add_parser("add", description="add an alias")
  alias_add_parser.add_argument("alias", type=str, help="alias name")
  alias_add_parser.add_argument("repository_uri", type=str, help="repository uri")
  alias_add_parser.add_argument("-f", "--file", help="Specify mimic wallet file to use")

  alias_rm_parser = alias_action_sub_parser.add_parser("rm", description="remove an alias")
  alias_rm_parser.add_argument("alias", type=str, help="alias name")
  alias_rm_parser.add_argument("-f", "--file", help="Specify mimic wallet file to use")

  alias_list_parser = alias_action_sub_parser.add_parser("list", description="list alias")
  alias_list_parser.add_argument("-f", "--file", help="Specify mimic wallet file to use")
  
  alias_init_parser = alias_action_sub_parser.add_parser("init", description="init new alias wallet")
  alias_init_parser.add_argument("-f", "--file", help="Specify mimic wallet file to use")

  init_parser = sub_parser.add_parser("init", description="setup a new mimic project template")
  init_parser.add_argument("project_dir", type=str, help="Specify the mimic project directory", nargs='?')

  preview_parser = sub_parser.add_parser("preview", description="Preview your mimic project template")
  preview_parser.add_argument("project_dir", type=str, help="Specify the mimic project directory", nargs='?')

  args = arg_parser.parse_args()

  command_options = None
  match args.command:
    case "clone":
      command_options = NewMimicCloneOptions({
        "out_dir": args.out_dir,
        "repository_uri": args.repository_uri,
        "unsafe_mode": args.unsafe,
        "alias_wallet_file_path": args.file
      })
    case "lint":
      command_options = NewMimicLintOptions({
        "project_dir": args.project_dir
      })
    case "alias": 
      command_options = NewMimicAliasOptions({
      "action": NewMimicAliasAction(args.action, args),
      "alias_wallet_file_path": args.file
    })
    case "init":
      command_options = NewMimicInitOptions({
        "project_dir": args.project_dir
      })
    case "preview":
      command_options = NewMimicPreviewOptions({
        "project_dir": args.project_dir
      })
    case _ as unknown:
      arg_parser.error(f'unknown command "{unknown}". Use -h,--help for usage information.')

  options = NewMimicOptions({
    "command": command_options,
    "debug": args.debug
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
