from cocotkit.cli.commands import BaseCommand
from cocotkit.io.reader import COCOReader
from cocotkit.coco import COCODataset
from cocotkit.query.queryset import Queryset
from cocotkit.resolver import MetadataResolver
from cocotkit.tasks import ImageCopyTask

class PartitionCommand(BaseCommand):
    name = "merge"
    help = "Merge multiple COCO JSON annotations files into a single one."

    def add_arguments(self, parser):
        parser.add_argument("files", nargs="+")

    def run(self, args):
        datasets = []
        for f in args.files:
            ds = COCOReader().read(f)

            datasets.append(ds)

        qs = Queryset(datasets)

        ds = qs.merge().export("coco", MetadataResolver("out/merged.json")).collect()