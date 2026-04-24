from cocotkit.cli.commands import BaseCommand


class StatsCommand(BaseCommand):
    name = "stats"
    help = "Show stats"

    def add_arguments(self, parser):
        parser.add_argument("file", help="COCO JSON file")

    def run(self, args):
        print(f"Stats about: {args.file}")
