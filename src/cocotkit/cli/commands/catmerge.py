from cocotkit.cli.commands import BaseCommand
from cocotkit.coco import COCODataset
from cocotkit.io.reader import COCOReader
from cocotkit.resolver import MetadataResolver


class CatMergeComand(BaseCommand):
    name = "catmerge"
    help = ""

    def add_arguments(self, parser):
        parser.add_argument("file", help="COCO JSON file")

    def run(self, args):
        dataset = COCOReader().read(args.file)

        res = dataset.query().merge_categories(categories__name__neq="Unclassified", to="Metazoa").export(format="coco", resolver=MetadataResolver(f"merged/{args.file}")).collect()