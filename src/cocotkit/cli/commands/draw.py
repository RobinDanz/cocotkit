from cocotkit.cli.commands import BaseCommand
from cocotkit.io.reader import COCOReader
from cocotkit.coco import COCODataset
from cocotkit.query.queryset import Queryset
from cocotkit.resolver import MetadataResolver
from cocotkit.tasks import ImageCopyTask
from cocotkit.tasks import DrawTask

class DrawCommand(BaseCommand):
    name = "draw"
    help = "Draw polygones an bbox"

    def add_arguments(self, parser):
        parser.add_argument("files", nargs="+")

    def run(self, args):
        datasets = []
        for f in args.files:
            ds = COCOReader().read(f)

            datasets.append(ds)

        qs = Queryset(datasets).filter(categories__name__neq="Unclassified").filter(categories__name__neq="Dirt").collect()

        DrawTask(
            images_root="C:\\Users\\Robin\\Pictures\\data\\coco\\images",
            output_root="out\\images"
        ).run(datasets)

        