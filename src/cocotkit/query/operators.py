from __future__ import annotations
from collections import defaultdict
from dataclasses import replace
from typing import TYPE_CHECKING
from pathlib import Path

import random

from operator import attrgetter

from cocotkit.query.expressions import QueryExpression, ExpressionParser

if TYPE_CHECKING:
    from cocotkit.coco import COCODataset
    from cocotkit.io.writer import BaseWriter

class QueryOperator:
    phase = 0
    requires_sync = False
    accepts_list = False

    def apply(self, dataset: COCODataset):
        raise NotImplementedError
    
    def set_context(self, **kwargs):
        self._extra_ctx = kwargs

class FilterOp(QueryOperator):
    phase = 5
    requires_sync = True

    def __init__(self, filters=None, expressions=None, parser=None):
        self.parser = parser or ExpressionParser()

        if expressions is not None:
            self.expressions = expressions
        else:
            self.expressions = [
                self.parser.parse(k, v)
                for k, v in (filters or {}).items()
            ]

        self.compiled = [self.build_predicate(e) for e in self.expressions]

    def merge(self, other: FilterOp):
        return FilterOp(expressions=self.expressions + other.expressions)

    @classmethod
    def from_specs(cls, expressions):
        return cls(expressions=expressions)
        
    def apply(self, dataset: COCODataset):
        return type(dataset)(
            images=self._filter(dataset.images, "images"),
            annotations=self._filter(dataset.annotations, "annotations"),
            categories=self._filter(dataset.categories, "categories"),
            meta=dataset.meta.copy()
        )

    def _filter(self, items, target):
        preds = [
            p for e, p in zip(self.expressions, self.compiled) 
            if e.target == target
        ]

        if not preds:
            return items

        return [
            item for item in items
            if all(p(item) for p in preds)
        ]

    @classmethod
    def build_predicate(self, expr: QueryExpression):
        getter = attrgetter(expr.field)
        op = expr.operator
        value = expr.value

        def predicate(obj):
            return op.apply(getter(obj), value)

        return predicate


class PipeOp(QueryOperator):
    phase = 10

    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def apply(self, dataset):
        return self.func(dataset, *self.args, **self.kwargs)


class SyncOp(QueryOperator):
    phase = 90

    def __init__(
        self,
        mode: str = "strict",
        keep_empty_images: bool = False,
        keep_empty_categories: bool = False
    ):
        self.mode = mode
        self.keep_empty_images = keep_empty_images
        self.keep_empty_categories = keep_empty_categories

    def apply(self, dataset: COCODataset):
        images = dataset.images
        annotations = dataset.annotations
        categories = dataset.categories

        image_ids = {img.id for img in images}
        category_ids = {cat.id for cat in categories}

        if self.mode == "strict":
            annotations = [
                a for a in annotations
                if a.image_id in image_ids
                and a.category_id in category_ids
            ]

        used_image_ids = {a.image_id for a in annotations}
        used_category_ids = {a.category_id for a in annotations}

        if self.keep_empty_images:
            new_images = images
        else:
            new_images = [
                img for img in images
                if img.id in used_image_ids
            ]
        
        if self.keep_empty_categories:
            new_categories = categories
        else:
            new_categories = [
                cat for cat in categories
                if cat.id in used_category_ids
            ]

        return type(dataset)(
            new_images, 
            annotations, 
            new_categories,
            meta=dataset.meta.copy()
        )


class SplitOp(QueryOperator):
    phase = 30
    
    TARGET_ALIASES = {
        "image": "images",
        "images": "images",
        "annotation": "annotations",
        "annotations": "annotations",
        "category": "categories",
        "categories": "categories",
    }

    def __init__(self, key: str):
        self.raw_key = key
        self.target, self.field = self._parse(key)
        self.getter = attrgetter(self.field)

    def _parse(self, key):
        parts = key.split("__")

        if len(parts) == 1:
            target = parts[0]
            field = "id"
        elif len(parts) == 2:
            target, field = parts
        else:
            raise ValueError(f"Invalid split key '{key}'. Expecter 'image' or 'image__field'")

        target = self.TARGET_ALIASES.get(target)

        if not target:
            raise ValueError(f"Unknown target '{parts[0]}'")

        return target, field

    def _validate_field(self, dataset: COCODataset):
        items = getattr(dataset, self.target)

        if not items:
            return

        sample = items[0]

        if not hasattr(sample, self.field):
            raise ValueError(f"Field '{self.field}' does not exist on '{self.target}'")

    def _build_dataset(self, dataset: COCODataset, grouped_items: list):
        if self.target == "annotations":
            anns = grouped_items
            image_ids = {a.image_id for a in anns}
            category_ids = {a.category_id for a in anns}

            return type(dataset)(
                images=[i for i in dataset.images if i.id in image_ids],
                annotations=anns,
                categories=[c for c in dataset.categories if c.id in category_ids],
                meta=dataset.meta.copy()
            ), "annotations"

        elif self.target == "images":
            imgs = grouped_items
            image_ids = {i.id for i in imgs}

            anns = [a for a in dataset.annotations if a.image_id in image_ids]
            category_ids = {a.category_id for a in anns}

            return type(dataset)(
                images=imgs,
                annotations=anns,
                categories=[c for c in dataset.categories if c.id in category_ids],
                meta=dataset.meta.copy()
            ), "images"

        elif self.target == "categories":
            cats = grouped_items
            cat_ids = {c.id for c in cats}

            anns = [a for a in dataset.annotations if a.category_id in cat_ids]
            image_ids = {a.image_id for a in anns}

            return type(dataset)(
                images=[i for i in dataset.images if i.id in image_ids],
                annotations=anns,
                categories=cats,
                meta=dataset.meta.copy()
            ), "categories"

        else:
            raise ValueError(f"Unsupported split target: {self.target}")

    def apply(self, dataset: COCODataset):
        self._validate_field(dataset)

        items = getattr(dataset, self.target)
        groups = defaultdict(list)

        for item in items:
            groups[self.getter(item)].append(item)

        results = []

        for i, (_, grouped_items) in enumerate(groups.items()):
            ds, split_type = self._build_dataset(dataset, grouped_items)

            name = ""

            if split_type == "annotations":
                if len(ds.annotations) > 0:
                    name = ds.annotations[0].id
            
            elif split_type == "categories":
                if len(ds.categories) > 0:
                    name = ds.categories[0].name

            elif split_type == "images":
                if len(ds.images) > 0:
                    name = Path(ds.images[0].file_name).stem

            ds.meta.update({
                "split_index": i,
                "name": name
            })

            results.append(ds)

        return results
    
class ExportOp(QueryOperator):
    phase = 1000
    
    def __init__(self, writer: BaseWriter, resolver):
        super().__init__()
        self.writer = writer
        self.resolver = resolver

    def apply(self, dataset: COCODataset | list):
        filename = self.resolver.resolve(dataset)

        if isinstance(dataset, list):
            self.writer.write_many(dataset, filename)
        else:
            self.writer.write_one(dataset, filename)

        return dataset
    
class UpdateOp(QueryOperator):
    phase = 20
    requires_sync = True

    def __init__(self, updates: dict, filters: dict, parser=None):
        self.parser = parser or ExpressionParser()

        self.expressions = [
            self.parser.parse(k, v)
            for k, v in (filters or {}).items()
        ]

        self.updates = updates

        targets = {e.target for e in self.expressions}

        if len(targets) != 1:
            raise ValueError("UpdateOp supports only one target")
        
        self.target = targets.pop()

        self.compiled = [self.build_predicate(e) for e in self.expressions]

    def build_predicate(self, expr: QueryExpression):
        getter = attrgetter(expr.field)
        op = expr.operator
        value = expr.value

        def predicate(obj):
            return op.apply(getter(obj), value)
        
        return predicate
    
    def _update_object(self, obj):
        data = obj.to_dict().copy()

        for field, value in self.updates.items():
            if callable(value):
                data[field] = value(obj)
            else:
                data[field] = value
        
        return type(obj)(**data)
    
    def apply(self, dataset: COCODataset):
        def update_items(items, target: str):
            if target != self.target:
                return items
            
            if not self.compiled:
                return items
            
            updated = []

            for obj in items:
                if all(pred(obj) for pred in self.compiled):
                    updated.append(self._update_object(obj))
                else:
                    updated.append(obj)
            
            return updated
        
        return type(dataset)(
            images=update_items(dataset.images, "images"),
            annotations=update_items(dataset.annotations, "annotations"),
            categories=update_items(dataset.categories, "categories"),
            meta=dataset.meta.copy()
        )
    
class MergeOp(QueryOperator):
    accepts_list = True
    phase = 1

    def apply(self, datasets: list[COCODataset]):
        images = []
        annotations = []
        categories = []

        image_offset = 0
        annotation_offset = 0

        category_name_to_id = {}
        next_category_id = 1

        for ds in datasets:
            local_category_map = {}

            for cat in ds.categories:
                if cat.name not in category_name_to_id:
                    category_name_to_id[cat.name] = next_category_id
                    categories.append(
                        type(cat)(
                            id=next_category_id,
                            name=cat.name
                        )
                    )

                    next_category_id += 1
                
                local_category_map[cat.id] = category_name_to_id[cat.name]

            for img in ds.images:
                new_img = type(img)(**{
                    **img.to_dict(),
                    "id": img.id + image_offset
                })

                images.append(new_img)

            for ann in ds.annotations:
                new_ann = type(ann)(**{
                    **ann.to_dict(),
                    "id": ann.id + annotation_offset,
                    "image_id": ann.image_id + image_offset,
                    "category_id": local_category_map[ann.category_id],
                    "segmentation": ann.segmentation
                })

                annotations.append(new_ann)
        
        return type(datasets[0])(images, annotations, categories, meta={})
    
class PartitionOp(QueryOperator):
    accepts_list = True
    phase = 100

    def __init__(
        self, 
        train=0.7,
        val=0.2,
        test=None,
        seed=42,
        shuffle=True
    ):
        self.train = train
        self.val = val
        self.test = test
        self.seed = seed
        self.shuffle = shuffle

    def apply(self, datasets: list[COCODataset]):
        if self.shuffle:
            random.seed(self.seed)
            random.shuffle(datasets)

        print(self.train)
        print(self.val)

        n = len(datasets)
        n_train = int(n * self.train)
        n_val = int(n * self.val)

        train_set = datasets[:n_train]
        val_set = datasets[n_train:n_train + n_val]
        test_set = datasets[n_train + n_val:]

        return [
            self._merge_group(train_set, "train"),
            self._merge_group(val_set, "val"),
            self._merge_group(test_set, "test"),
        ]
    
    def _merge_group(self, datasets: list[COCODataset], name):
        images = []
        annotations = []
        categories = datasets[0].categories if datasets else []

        for ds in datasets:
            images.extend(ds.images)
            annotations.extend(ds.annotations)

        return type(datasets[0])(
            images=images,
            annotations=annotations,
            categories=categories,
            meta={"split": name}
        )
    
class MergeCategoriesOp(QueryOperator):
    requires_sync = True
    phase = 20

    def __init__(
        self, 
        filters: dict,
        to: str,
        parser=None
    ):
        self.to = to

        self.parser = parser or ExpressionParser()

        self.expressions = [
            self.parser.parse(k, v)
            for k, v in (filters or {}).items()
        ]

        targets = {e.target for e in self.expressions}

        if targets != {"categories"}:
            raise ValueError(
                "MergeCategoriesOp only supports category filters"
            )
        
        self.compiled = [
            self.build_predicate(e)
            for e in self.expressions
        ]

    def apply(self, dataset: COCODataset):

        categories_to_merge = [
            c for c in dataset.categories
            if all(pred(c) for pred in self.compiled)
        ]

        if not categories_to_merge:
            return dataset
        
        merge_ids = {c.id for c in categories_to_merge}

        target = next(
            (
                c for c in dataset.categories
                if c.name == self.to
            ),
            None
        )

        if target is None:
            max_id = max(
                (c.id for c in dataset.categories),
                default = 0
            )

            target = type(dataset.categories[0])(
                id=max_id + 1,
                name=self.to
            )

            categories = dataset.categories + [target]

        else:
            categories = list(dataset.categories)

        target_id = target.id

        updated_annotations = []

        for ann in dataset.annotations:
            if ann.category_id in merge_ids:
                ann = replace(
                    ann,
                    category_id=target_id
                )
            
            updated_annotations.append(ann)
        
        updated_categories = [
            c for c in categories
            if (
                c.id not in merge_ids
                or c.id == target_id
            )
        ]

        return type(dataset)(
            images=dataset.images,
            annotations=updated_annotations,
            categories=updated_categories,
            meta=dataset.meta.copy()
        )

    def build_predicate(self, expr: QueryExpression):
        getter = attrgetter(expr.field)
        op = expr.operator
        value = expr.value

        def predicate(obj):
            return op.apply(getter(obj), value)
        
        return predicate