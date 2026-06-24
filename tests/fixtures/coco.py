import pytest

from cocotkit.coco import (
    COCODataset,
    COCOImage,
    COCOAnnotation,
    COCOCategory
)

@pytest.fixture
def sample_image_dict():
    return {
        "id": 123,
        "file_name": "test.png",
        "height": 1000,
        "width": 2000,
    }

@pytest.fixture
def sample_annotation_dict():
    return {
        "id": 123,
        "iscrowd": 1,
        "area": 16,
        "image_id": 1, 
        "category_id": 2, 
        "bbox": [0, 3, 8, 7],
        "segmentation": [[0, 10, 4, 9, 8, 9, 3, 3, 0, 10]]
    }

@pytest.fixture
def sample_category_dict():
    return {
        "id": 123,
        "name": "somename"
    }

@pytest.fixture
def sample_dataset_dict():
    return {
        "images": [
        {
            "id": 123,
            "file_name": "test.png",
            "height": 1000,
            "width": 2000,
        },
        {
            "id": 124,
            "file_name": "test2.png",
            "height": 3000,
            "width": 4000,
        }
    ],
    "annotations": [
        {
            "id": 131,
            "iscrowd": 1,
            "area": 16,
            "image_id": 123, 
            "category_id": 141, 
            "bbox": [0, 3, 8, 7],
            "segmentation": [[0, 10, 4, 9, 8, 9, 3, 3, 0, 10]]
        },
        {
            "id": 132,
            "iscrowd": 1,
            "area": 16,
            "image_id": 124, 
            "category_id": 142, 
            "bbox": [0, 4, 9, 7],
            "segmentation": [[0, 10, 4, 11, 9, 8, 7, 6, 3, 4, 0, 10]]
        },
    ],
    "categories": [
            {
                "id": 141,
                "name": "somename"
            },
            {
                "id": 142,
                "name": "anothername"
            }
        ]
    }

@pytest.fixture
def sample_coco_image(sample_image_dict):
    return COCOImage.from_dict(sample_image_dict)

@pytest.fixture
def sample_coco_annotation(sample_annotation_dict):
    return COCOAnnotation.from_dict(
        sample_annotation_dict
    )

@pytest.fixture
def sample_coco_category(sample_category_dict):
    return COCOCategory.from_dict(sample_category_dict)

@pytest.fixture
def sample_coco_dataset(sample_dataset_dict):
    return COCODataset.from_dict(sample_dataset_dict)