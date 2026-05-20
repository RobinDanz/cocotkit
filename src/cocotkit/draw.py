from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from cocotkit.coco import COCOAnnotation, COCOCategory, COCOImage

from abc import ABC, abstractmethod
from PIL import ImageDraw

class BaseDrawer(ABC):    
    @abstractmethod
    def draw(
        self,
        image,
        annotations,
        categories
    ):
        raise NotImplementedError
    
class PILDrawer(BaseDrawer):

    def draw(self, image, annotations: List[COCOAnnotation], categories: List[COCOCategory]):
        draw = ImageDraw.Draw(image)

        cat_map = {
            c.id: c.name
            for c in categories
        }

        for ann in annotations:
            if ann.bbox:
                x,y,w,h = ann.bbox

                draw.rectangle(
                    [x, y, x + w, y + h],
                    outline="red",
                    width=2
                )

            if ann.segmentation:
                for poly in ann.segmentation:
                    points = [
                        (poly[i], poly[i + 1])
                        for i in range(0, len(poly), 2)
                    ]

                    draw.polygon(
                        points,
                        outline="green"
                    )

        return image