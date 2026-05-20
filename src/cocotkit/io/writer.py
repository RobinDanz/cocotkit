from __future__ import annotations
from typing import TYPE_CHECKING

import os
import orjson
from typing import Dict, Any

if TYPE_CHECKING:
    from cocotkit.coco import Serializable

from abc import ABC, abstractmethod

from cocotkit.converters.yolo import COCOToYOLOConverter


class BaseWriter(ABC):
    @abstractmethod
    def write_one(self, data: Serializable | Dict[str, Any], filename: str):
        pass

    def write_many(self, data, pattern: str):
        for i, item in enumerate(data):
            filename = pattern.format(i=i)
            self.write_one(item, filename)


class COCOWriter(BaseWriter):
    def __init__(self, indent=False):
        self.indent = indent

    def _serialize(self, data: Serializable | Dict[str, Any]):
        if hasattr(data, "to_dict"):
            data = data.to_dict()

        option = orjson.OPT_INDENT_2 if self.indent else 0
        return orjson.dumps(data, option=option)

    def write_one(self, data: Serializable | Dict[str, Any], filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "wb") as f:
            f.write(self._serialize(data))


class YOLOWriter(BaseWriter):
    def __init__(self, converter=None):
        self.converter = converter or COCOToYOLOConverter()

    def write_one(self, data: Serializable | Dict[str, Any], output_dir: str):
        os.makedirs(output_dir, exist_ok=True)

        data = self.converter.convert(data)

        for image_name, lines in data.items():
            txt_name = os.path.splitext(image_name)[0] + ".txt"
            path = os.path.join(output_dir, txt_name)

            with open(path, "w") as f:
                f.write("\n".join(lines))

class WriterFactory:
    @staticmethod
    def create(format: str, **kwargs):
        if format == "coco":
            return COCOWriter(**kwargs)
        elif format == "yolo":
            return YOLOWriter(**kwargs)
        else:
            raise ValueError(f"Unknown format: {format}")
