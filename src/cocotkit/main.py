import argparse

from cocotkit.cli.registry import discover_commands


def main():
    parser = argparse.ArgumentParser(prog="cocotkit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    commands = {}

    for cmd_cls in discover_commands():
        cmd = cmd_cls()
        subparser = subparsers.add_parser(cmd.name, help=cmd.help)
        cmd.add_arguments(subparser)
        commands[cmd.name] = cmd

    args = parser.parse_args()

    command = commands[args.command]
    command.run(args)
    
    
if __name__ == "__main__":
    main()
