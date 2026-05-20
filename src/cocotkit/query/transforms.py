from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cocotkit.coco import COCODataset

class BaseTransform:
    def apply(self, dataset: COCODataset):
        raise NotImplementedError
    
class UpdateTransform:

    def __init__(self, expressions, updater):
        self.expressions = expressions
        self.updater = updater

    def apply(self, dataset):

        new_categories = []

        for cat in dataset.categories:

            if any(expr.match(cat) for expr in self._exprs_for("category")):
                new_cat = self.updater(cat)
            else:
                new_cat = cat

            new_categories.append(new_cat)

        return dataset.__class__(
            images=dataset.images,
            annotations=dataset.annotations,
            categories=new_categories,
            meta=dataset.meta.copy()
        )

    def _exprs_for(self, target):
        return [e for e in self.expressions if e.target == target]
