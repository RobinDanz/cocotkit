from cocotkit.cli.commands import BaseCommand
from cocotkit.io.reader import COCOReader
from cocotkit.coco import COCODataset
from cocotkit.query.queryset import Queryset
from cocotkit.resolver import MetadataResolver
from cocotkit.tasks import ImageCopyTask

class PartitionCommand(BaseCommand):
    name = "partition"
    help = "Splits one or multiple COCO JSON into train/test/validation sets"

    def add_arguments(self, parser):
        parser.add_argument("files", nargs="+")

    def run(self, args):
        datasets = []
        for f in args.files:
            ds = COCOReader().read(f)

            datasets.append(ds)

        qs = Queryset(datasets)

        ds = qs.merge().split("images").partition().export("coco", MetadataResolver("out/{split}/annotations.json")).collect()

        ImageCopyTask("C:\\Users\\Robin\\Pictures\\data\\coco\\images", "C:\\Users\\Robin\\Pictures\\data\\coco\\images\\splits").run(ds)