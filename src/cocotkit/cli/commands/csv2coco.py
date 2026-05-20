from cocotkit.cli.commands import BaseCommand
from cocotkit.io.reader import CSVReader
from cocotkit.coco import COCODataset
from cocotkit.resolver import MetadataResolver


class CSV2COCO(BaseCommand):
    name = "csv2coco"
    help = """
        Converts a CSV annotation file to a COCO JSON file

        CSV must contain following lines
    """

    def add_arguments(self, parser):
        parser.add_argument("file", help="CSV file")

    def run(self, args):
        dataset = CSVReader().read(args.file)

        dataset.query().export(format="coco", resolver=MetadataResolver("out/test.json")).collect()
