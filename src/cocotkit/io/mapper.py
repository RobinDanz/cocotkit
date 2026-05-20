import json

class ColumnMapper:
    def __init__(self, source, default):
        self.source = source
        self.default = default

    def map(self, value, **kwargs):
        return value

class SegmentationMapper(ColumnMapper):
    def map(self, value, **kwargs):
        loaded = json.loads(value)
        if isinstance(loaded, list):
            return [loaded]
        return self.default
    
class BboxMapper(ColumnMapper):
    def map(self, value, **kwargs):
        points = json.loads(kwargs.get("points", []))

        if len(points) < 4:
            return self.default

        xs = points[0::2]
        ys = points[1::2]

        x_min = min(xs)
        y_min = min(ys)
        x_max = max(xs)
        y_max = max(ys)

        return (
            x_min,
            y_min,
            x_max - x_min,
            y_max - y_min,
        )
    
class AreaMapper(ColumnMapper):
    def map(self, value, **kwargs):
        points = json.loads(kwargs.get("points", []))

        if len(points) < 4:
            return self.default
        
        xs = points[0::2]
        ys = points[1::2]

        coords = list(zip(xs, ys))

        area = 0
        n = len(coords)

        for i in range(n):
            x1, y1 = coords[i]
            x2, y2 = coords[(i + 1) % n]

            area += x1 * y2
            area -= y1 * x2

        return abs(area) / 2
    

class DefaultCSVMapper:
    COLUMN_MAP: dict[str, ColumnMapper] = {
        "category": ColumnMapper("label_name", ""),
        "category_id": ColumnMapper("label_id", 0),
        "file_name": ColumnMapper("filename", ""),
        "width": ColumnMapper("image_width", 0),
        "height": ColumnMapper("image_height", 0),
        "segmentation": SegmentationMapper("points", [[]]),
        "bbox": BboxMapper("bbox", []),
        "area": AreaMapper("area", 0),
        "iscrowd": ColumnMapper("iscrowd", 0)
    }

    def map_row(self, row: dict):
        mapped = {}

        for target, column_mapper in self.COLUMN_MAP.items():
            value = row.get(column_mapper.source, column_mapper.default)
            mapped[target] = column_mapper.map(value, **row)

        return mapped