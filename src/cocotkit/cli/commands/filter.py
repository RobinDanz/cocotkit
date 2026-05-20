from cocotkit.cli.commands import BaseCommand
from cocotkit.io.reader import COCOReader
from cocotkit.coco import COCODataset
from cocotkit.resolver import MetadataResolver


class FilterCommand(BaseCommand):
    name = "filter"
    help = "Filters a COCO JSON file"

    def add_arguments(self, parser):
        parser.add_argument("file", help="COCO JSON file")

    def run(self, args):
        dataset = COCOReader().read(args.file)

        res = dataset.query().filter(categories__name__neq="Unclassified").export(format="coco", resolver=MetadataResolver("out/test.json")).collect()
