from cocotkit.cli.commands import BaseCommand
from cocotkit.coco import COCODataset
from cocotkit.io.reader import COCOReader
from cocotkit.resolver import MetadataResolver


class ConvertCommand(BaseCommand):
    name = "convert"
    help = ""

    def add_arguments(self, parser):
        parser.add_argument("file", help="COCO JSON file")

    def run(self, args):
        dataset = COCOReader.read(args.file)

        res = dataset.query().update(categories__name="Default", set={"name": "Undefined"}).export(format="coco", resolver=MetadataResolver("out/test.json")).collect()