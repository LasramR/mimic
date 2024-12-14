from argparse import ArgumentParser

from orca.cmd.clone import clone
from orca.options import NewOrcaCloneOptions, NewOrcaOptions

def main():
  arg_parser = ArgumentParser(prog="orca")

  arg_parser.add_argument("-d", "--debug", action='store_true', help="Enable schr debug mode which displays compiler/linker commands during execution\ndisabled by default", required=False)

  sub_parser = arg_parser.add_subparsers(dest="command", required=True)
  
  clone_parser = sub_parser.add_parser("clone", description="clone repository")
  clone_parser.add_argument("repository_url", type=str, help="URL of the repository to clone")
  clone_parser.add_argument("out_dir", type=str, help="Specify the output directory", nargs='?')

  args = arg_parser.parse_args()

  command_options = None
  match args.command:
    case "clone":
      command_options = NewOrcaCloneOptions({
        "out_dir": args.out_dir,
        "repository_url": args.repository_url
      })
    case _ as unknown:
      arg_parser.error(f'unknown command "{unknown}". Use -h,--help for usage information.')

  options = NewOrcaOptions({
    "command": command_options,
    "debug": args.debug
  })

  try:
    match(options["command"]["name"]):
      case "clone":
        clone(options)
      case _ as unknown:
        options["logger"].error(f'unknown command "{unknown}". Use -h,--help for usage information.')
        exit(1)
  except Exception as e:
    options["logger"].error(e)
    exit(1)

if __name__ == "__main__":
  main()
