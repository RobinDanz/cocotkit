from cocotkit.query.expressions import (
    EqOperator,
    NeqOperator,
    GtOperator,
    GteOperator,
    LtOperator,
    LteOperator,
    InOperator,
    NinOperator,
    ContainsOperator,
    OperatorRegistry,
    ExpressionParser,
    QueryExpression
)

import pytest

class TestEqOperator:
    def test_name(self):
        op = EqOperator()

        assert op.name == "eq"

    def test_apply(self):
        op = EqOperator()

        assert op.apply(1, 1)
        assert not op.apply(1, 2)

        assert op.apply("a", "a")
        assert not op.apply("a", "b")

        assert op.apply(True, True)
        assert not op.apply(True, False)

class TestNeqOperator:
    def test_name(self):
        op = NeqOperator()

        assert op.name == "neq"

    def test_apply(self):
        op = NeqOperator()

        assert not op.apply(1, 1)
        assert op.apply(1, 2)

        assert not op.apply("a", "a")
        assert op.apply("a", "b")

        assert not op.apply(True, True)
        assert op.apply(True, False)

class TestGtOperator:
    def test_name(self):
        op = GtOperator()

        assert op.name == "gt"

    def test_apply(self):
        op = GtOperator()

        assert op.apply(1, 0)
        assert not op.apply(1, 1)
        assert not op.apply(1, 2)

class TestGteOperator:
    def test_name(self):
        op = GteOperator()

        assert op.name == "gte"

    def test_apply(self):
        op = GteOperator()

        assert op.apply(1, 0)
        assert op.apply(1, 1)
        assert not op.apply(1, 2)

class TestLtOperator:
    def test_name(self):
        op = LtOperator()

        assert op.name == "lt"

    def test_apply(self):
        op = LtOperator()

        assert op.apply(0, 1)
        assert not op.apply(1, 1)
        assert not op.apply(2, 1)

class TestLteOperator:
    def test_name(self):
        op = LteOperator()

        assert op.name == "lte"

    def test_apply(self):
        op = LteOperator()

        assert op.apply(0, 1)
        assert op.apply(1, 1)
        assert not op.apply(2, 1)

class TestInOperator:
    def test_name(self):
        op = InOperator()

        assert op.name == "in"

    def test_apply(self):
        op = InOperator()

        assert op.apply(1, [1, 2, 3])
        assert op.apply("hello", ["a", "b", "hello", "banana"])

        assert not op.apply(1, [10, 15, 20])
        assert not op.apply("hello", ["a", "b", "banana"])

class TestNinOperator:
    def test_name(self):
        op = NinOperator()

        assert op.name == "nin"

    def test_apply(self):
        op = NinOperator()
        
        assert not op.apply(1, [1, 2, 3])
        assert not op.apply("hello", ["a", "b", "hello", "banana"])

        assert op.apply(1, [10, 15, 20])
        assert op.apply("hello", ["a", "b", "banana"])

class TestContainsOperator:
    def test_name(self):
        op = ContainsOperator()

        assert op.name == "contains"

    def test_apply(self):
        op = ContainsOperator()

        assert op.apply([1, 2, 3], 1)
        assert op.apply(["a", "b", "hello", "banana"], "hello")

        assert not op.apply([10, 15, 20], 1)
        assert not op.apply(["a", "b", "banana"], "hello")

class TestOperatorRegistry:
    operators = {
        "eq": EqOperator,
        "neq": NeqOperator,
        "gt": GtOperator,
        "gte": GteOperator,
        "lt": LtOperator,
        "lte": LteOperator,
        "in": InOperator,
        "nin": NinOperator,
        "contains": ContainsOperator,
    }

    def test_has_all_operators(self):
        for name, op in OperatorRegistry._ops.items():
            assert name in self.operators.keys()
            assert isinstance(op, self.operators[name])

    def test_get(self):
        for name, op in self.operators.items():
            result_op = OperatorRegistry.get(name)

            assert isinstance(result_op, op)

    def test_get_fails(self):
        with pytest.raises(ValueError) as excinfo:
            OperatorRegistry.get("random_op")

        assert "Unknown operator" in str(excinfo)

class TestQueryExpression:
    def test_init(self):
        qexpr = QueryExpression(
            target="images",
            field="width",
            operator=EqOperator(),
            value=1000
        )

        assert qexpr.target is "images"
        assert qexpr.field is "width"
        assert isinstance(qexpr.operator, EqOperator)
        assert qexpr.value == 1000

    def test_match(self, sample_coco_image):
        qexpr = QueryExpression(
            target="images",
            field="width",
            operator=EqOperator(),
            value=2000
        )

        assert qexpr.match(sample_coco_image)

        qexpr = QueryExpression(
            target="images",
            field="width",
            operator=GtOperator(),
            value=3000
        )

        assert not qexpr.match(sample_coco_image)



class TestExpressionParser:
    parser = ExpressionParser()

    def test_validate_target(self):
        targets = [
            "images",
            "annotations",
            "categories"
        ]

        for target in targets:
            self.parser.validate_target(target)

        with pytest.raises(ValueError) as excinfo:
            self.parser.validate_target("hello")

        assert "Invalid target" in str(excinfo)

    def test_parse_base(self):
        expr = "images__width"
        value = 1000

        qexpr = self.parser.parse(expr, value)
        
        assert isinstance(qexpr, QueryExpression)

        assert qexpr.target == "images"
        assert qexpr.field == "width"
        assert isinstance(qexpr.operator, EqOperator)
        assert qexpr.value == value

    def test_parse(self):
        expr = "annotations__category_id__in"
        value = [1, 2, 3, 4]

        qexpr = self.parser.parse(expr, value)

        assert isinstance(qexpr, QueryExpression)

        assert qexpr.target == "annotations"
        assert qexpr.field == "category_id"
        assert isinstance(qexpr.operator, InOperator)
        assert qexpr.value == value

    def test_parse_fail(self):
        expr = "some__invalid__expression__length"
        value = 1

        with pytest.raises(ValueError) as excinfo:
            self.parser.parse(expr, value)
        
        assert "Invalid expression" in str(excinfo.value)