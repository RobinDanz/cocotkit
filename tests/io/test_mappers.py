from cocotkit.io.mapper import (
    ColumnMapper,
    SegmentationMapper,
    BboxMapper,
    AreaMapper,
    DefaultCSVMapper
)

import json

class TestColumnMapper:
    def test_init(self):
        mapper = ColumnMapper("some_column", "some_default_value")

        assert mapper.source == "some_column"
        assert mapper.default == "some_default_value"

    def test_map(self):
        mapper = ColumnMapper("column1", "default1")

        out = mapper.map("hello")

        assert out == "hello"

class TestSegmentationMapper:
    def test_map(self):
        value = [0, 10, 4, 9, 8, 9, 3, 3, 0, 10]
        str_value = json.dumps(value)

        mapper = SegmentationMapper("some_column", [[]])

        out = mapper.map(str_value)

        assert isinstance(out, list)
        assert out == [value]

    def test_map_default(self):
        value = {"key": "val"}

        mapper = SegmentationMapper("", [[]])

        out = mapper.map(json.dumps(value))

        assert isinstance(out, list)
        assert out == [[]]

class TestBboxMapper:
    def test_map(self):
        value = {"points": json.dumps([0, 10, 4, 11, 9, 8, 7, 6, 3, 4, 0, 10])}
        mapper = BboxMapper("bbox", [])

        out = mapper.map([], **value)
        

        assert out == [0, 4, 9, 7]


    def test_map_default(self):
        value = {"points": json.dumps([0])}

        mapper = BboxMapper("bbox", [])

        out = mapper.map([], **value)

        assert out == []







