import pytest

from cocotkit.coco import COCODataset, COCOImage, COCOCategory, COCOAnnotation
from cocotkit.query.queryset import Queryset

class TestCOCOImage:
    def test_base(self):
        img = COCOImage()

        assert img.id == 0
        assert img.file_name == ""
        assert img.height == 0
        assert img.width == 0
        assert not img.longitude
        assert not img.latitude

    def test_from_dict(self, sample_image_dict):
        img = COCOImage.from_dict(sample_image_dict)

        assert img.id == 123
        assert img.file_name == "test.png"
        assert img.height == 1000
        assert img.width == 2000
        assert not img.latitude
        assert not img.longitude

    def test_to_dict(self, sample_coco_image):
        img = sample_coco_image.to_dict()

class TestCOCOCategory:

    def test_base(self):
        cat = COCOCategory()

        assert cat.id == 0
        assert cat.name == ""
        assert cat.supercategory == ""

    def test_from_dict(self, sample_category_dict):

        cat = COCOCategory.from_dict(sample_category_dict)

        assert cat.id == 123
        assert cat.name == "somename"
        assert cat.supercategory == ""

    def test_to_dict(self, sample_coco_category):
        cat = sample_coco_category.to_dict()

class TestCOCOAnnotation:

    def test_base(self):
        ann = COCOAnnotation()

        assert ann.id == 0
        assert ann.iscrowd == 0
        assert ann.area == 0
        assert ann.image_id == 0
        assert ann.category_id == 0
        assert ann.bbox == ()
        assert ann.segmentation == []

    def test_from_dict(self, sample_annotation_dict):

        ann = COCOAnnotation.from_dict(sample_annotation_dict)

        assert ann.id == 123
        assert ann.iscrowd == 1
        assert ann.area == 16
        assert ann.image_id == 1
        assert ann.category_id == 2
        assert ann.bbox == [0, 3, 8, 7]
        assert ann.segmentation == [[0, 10, 4, 9, 8, 9, 3, 3, 0, 10]]

    def test_to_dict(self, sample_coco_annotation):
        ann = sample_coco_annotation.to_dict()

class TestCOCODataset:

    def test_base(self):
        ds = COCODataset()

        assert ds.images == []
        assert ds.annotations == []
        assert ds.categories == []
        assert ds.meta == {}

    def test_from_dict(self, sample_dataset_dict):
        ds = COCODataset.from_dict(sample_dataset_dict)

        assert len(ds.images) == 2
        assert len(ds.annotations) == 2
        assert len(ds.categories) == 2

    def test_to_dict(self, sample_coco_dataset):
        ds = sample_coco_dataset.to_dict()

    def test_query(self, sample_coco_dataset):
        q = sample_coco_dataset.query()

        assert isinstance(q, Queryset)