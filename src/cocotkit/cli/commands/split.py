from cocotkit.cli.commands import BaseCommand
from cocotkit.split import COCOSplitter
from cocotkit.io.reader import COCOReader


class SplitCommand(BaseCommand):
    name = "split"
    help = "Splits a COCO JSON file into multiple files"

    def add_arguments(self, parser):
        parser.add_argument("file", help="COCO JSON file")

    def run(self, args):
        data = COCOReader.read(args.file)
        
        splitter = COCOSplitter()
        splitter.split(data)
