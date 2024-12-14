from argparse import ArgumentParser
from signal import SIGINT, signal

from orca.cmd.clone import clone
from orca.cmd.lint import lint
from orca.options import NewOrcaCloneOptions, NewOrcaLintOptions, NewOrcaOptions

def main():
  signal(SIGINT, lambda _a, _b: print() or exit(-1))
  arg_parser = ArgumentParser(prog="orca")

  arg_parser.add_argument("-d", "--debug", action='store_true', help="Enable schr debug mode which displays compiler/linker commands during execution\ndisabled by default", required=False)

  sub_parser = arg_parser.add_subparsers(dest="command", required=True)
  
  clone_parser = sub_parser.add_parser("clone", description="clone repository")
  clone_parser.add_argument("repository_url", type=str, help="URL of the repository to clone")
  clone_parser.add_argument("out_dir", type=str, help="Specify the output directory", nargs='?')
  clone_parser.add_argument("-u", "--unsafe", action="store_true", help="Enable unsafe mode, hooks will run without user confirmation")

  lint_parser = sub_parser.add_parser("lint", description="lint orca template")
  lint_parser.add_argument("project_dir", type=str, help="Specify the orca project directory", nargs='?')

  args = arg_parser.parse_args()

  command_options = None
  match args.command:
    case "clone":
      command_options = NewOrcaCloneOptions({
        "out_dir": args.out_dir,
        "repository_url": args.repository_url,
        "unsafe_mode": args.unsafe
      })
    case "lint":
      command_options = NewOrcaLintOptions({
        "project_dir": args.project_dir
      })
    case _ as unknown:
      arg_parser.error(f'unknown command "{unknown}". Use -h,--help for usage information.')

  options = NewOrcaOptions({
    "command": command_options,
    "debug": args.debug
  })

  result = False
  try:
    match(options["command"]["name"]):
      case "clone":
        result = clone(options)
      case "lint":
        result = lint(options)
      case _ as unknown:
        options["logger"].error(f'unknown command "{unknown}". Use -h,--help for usage information.')
  except Exception as e:
    options["logger"].error(e)

  exit(0 if result else 1)

if __name__ == "__main__":
  main()
