import json
import csv
from typing import Dict, Any

from abc import ABC, abstractmethod

from pathlib import Path

from cocotkit.coco import COCODataset, COCOImage, COCOCategory, COCOAnnotation
from cocotkit.io.mapper import DefaultCSVMapper

class FileReader(ABC):
    def __init__(self, validate=True):
        self.validate = validate

    def read(self, file) -> COCODataset:
        path = Path(file)

        if not path.exists() or not path.is_file():
            raise ValueError(f"File does not exists or is not a file: {path}")

        data = self._read(path)

        if self.validate:
            self._validate(data)

        return self._convert(data, path)

    @abstractmethod
    def _read(self, path: Path):
        pass

    def _validate(self, data):
        return True
    
    def _convert(self, data) -> COCODataset:
        return data


class COCOReader(FileReader):
    def _read(self, path: Path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
        
    def _convert(self, data: Dict[str, Any], path: Path):
        return COCODataset(
            images=[
                COCOImage(**img) for img in data.get("images", [])
            ],
            annotations=[
                COCOAnnotation(**ann) for ann in data.get("annotations", [])
            ],
            categories=[
                COCOCategory(**cat) for cat in data.get("categories", [])
            ],
            meta={
                "source_file": str(path)
            }
        )
    
class CSVReader(FileReader):
    def __init__(
        self,
        mapper=None,
        validate=True
    ):
        super().__init__(validate)

        self.mapper = mapper or DefaultCSVMapper()
        
    def _read(self, path: Path):
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
        
    def _convert(self, rows, path):
        annotations: list[COCOAnnotation] = []
        images: dict[str, COCOImage] = {}
        categories: dict[str, COCOCategory] = {}

        image_id = 0
        annotation_id = 1

        for row in rows:
            data = self.mapper.map_row(row)

            image_name = data["file_name"]
            category_name = data["category"]

            if image_name not in images:
                image_id += 1
                images[image_name] = COCOImage(
                    id=image_id,
                    file_name=data["file_name"],
                    width=int(data["width"]),
                    height=int(data["height"])
                )

            if category_name not in categories:
                categories[category_name] = COCOCategory(
                    id=len(categories) + 1,
                    name=category_name
                )

            cat_id = categories[category_name].id

            ann = COCOAnnotation(
                id=annotation_id,
                image_id=image_id,
                category_id=cat_id,
                segmentation=data["segmentation"],
                bbox=data["bbox"],
                area=data["area"],
                iscrowd=data["iscrowd"]
            )

            annotations.append(ann)

            annotation_id +=1

        return COCODataset(
            images=list(images.values()),
            annotations=annotations,
            categories=list(categories.values()),
            meta={
                "source_file": str(path)
            }
        )
