from cocotkit.query.operators import (
    FilterOp,
    PipeOp,
    SyncOp,
    SplitOp,
    ExportOp,
    UpdateOp,
    MergeOp,
    PartitionOp,
    MergeCategoriesOp
)
from cocotkit.io.writer import WriterFactory


class Queryset:
    def __init__(self, dataset, ops=None):
        self.dataset = dataset
        self.ops = ops or []

    def _clone(self, op):
        return Queryset(self.dataset, self.ops + [op])

    def filter(self, **kwargs):
        return self._clone(FilterOp(kwargs))

    def pipe(self, func, *args, **kwargs):
        return self._clone(PipeOp(func, args, kwargs))

    def split(self, key: str):
        return self._clone(SplitOp(key))
    
    def export(self, format="coco", resolver=None, **kwargs):
        writer = WriterFactory.create(format, **kwargs)
        return self._clone(ExportOp(writer, resolver))
    
    def update(self, set: dict, **filters):
        return self._clone(UpdateOp(set, filters))
    
    def merge(self, **kwargs):
        return self._clone(MergeOp())
    
    def merge_categories(self, to: str, **filters):
        return self._clone(
            MergeCategoriesOp(filters=filters, to=to)
        )
    
    def partition(self, **kwargs):
        return self._clone(PartitionOp(**kwargs))
    
    def delete(self):
        return self._clone()

    def collect(self):
        data = self.dataset
        ops = QueryOptimizer().optimize(self.ops)

        for op in ops:
            if isinstance(data, list) and not op.accepts_list:
                data = [op.apply(d) for d in data]

                # flatten
                flattened = []
                for item in data:
                    if isinstance(item, list):
                        flattened.extend(item)
                    else:
                        flattened.append(item)

                data = flattened
            else:
                data = op.apply(data)

        return data


class QueryOptimizer:
    def optimize(self, ops):
        optimized = []
        current_filter = None
        need_sync = False

        for op in ops:
            if isinstance(op, FilterOp):
                need_sync = True
                if current_filter is None:
                    current_filter = op
                else:
                    current_filter = current_filter.merge(op)
            else:
                if current_filter:
                    optimized.append(current_filter)
                    current_filter = None
                optimized.append(op)

        if current_filter:
            optimized.append(current_filter)

        if need_sync:
            optimized.append(SyncOp())

        optimized.sort(key=lambda op: op.phase)

        return optimized
