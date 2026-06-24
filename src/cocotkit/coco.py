from cocotkit.query.queryset import Queryset
from dataclasses import dataclass, asdict, field, fields
from typing import List, Tuple, Dict, Any, TypeVar, Type
from abc import ABC, abstractmethod

T = TypeVar("T", bound="Serializable")


class Serializable(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        return cls(**data)


class COCOData(Serializable):
    def to_dict(self):
        result = {}

        for f in fields(self):
            if f.metadata.get("serialize", True):
                value = getattr(self, f.name)

                if isinstance(value, list):
                    value = [
                        v.to_dict() if hasattr(v, "to_dict") else v
                        for v in value
                    ]
                elif hasattr(value, "to_dict"):
                    value = value.to_dict()

                result[f.name] = value

        return result


@dataclass
class COCOImage(COCOData):
    id: int = 0
    file_name: str = ""
    height: int = 0
    width: int = 0
    longitude: str | None = None
    latitude: str | None = None


@dataclass
class COCOAnnotation(COCOData):
    bbox: Tuple[int, int, int, int] = field(default_factory=tuple)
    segmentation: List = field(default_factory=list)
    id: int = 0
    iscrowd: int = 0
    area: int = 0
    image_id: int = 0
    category_id: int = 0


@dataclass
class COCOCategory(COCOData):
    id: int = 0
    name: str = ""
    supercategory: str = ""


@dataclass
class COCODataset(COCOData):
    images: List[COCOImage] = field(default_factory=list)
    annotations: List[COCOAnnotation] = field(default_factory=list)
    categories: List[COCOCategory] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict, metadata={"serialize": False})

    @classmethod
    def from_dict(cls, data: dict) -> "COCODataset":
        images = [COCOImage(**img) for img in data.get("images", [])]
        annotations = [COCOAnnotation(**ann) for ann in data.get("annotations", [])]
        categories = [COCOCategory(**cat) for cat in data.get("categories", [])]

        return cls(images=images, annotations=annotations, categories=categories)

    def query(self):
        return Queryset(self)
