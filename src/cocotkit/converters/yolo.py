from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cocotkit.coco import COCODataset


class COCOToYOLOConverter:
    def convert(self, dataset: COCODataset):
        result = {}

        image_map = {img.id: img for img in dataset.images}

        for ann in dataset.annotations:
            img = image_map[ann.image_id]

            x, y, w, h = ann.bbox
            W, H = img.width, img.height

            x_center = (x + w / 2) / W
            y_center = (y + h / 2) / H
            w /= W
            h /= H

            line = f"{ann.category_id} {x_center} {y_center} {w} {h}"

            result.setdefault(img.file_name, []).append(line)

        return result
