from abc import ABC, abstractmethod
from dataclasses import dataclass


class BaseOperator(ABC):
    name: str

    @abstractmethod
    def apply(self, field_Value, query_value) -> bool:
        pass

    def validate(self, query_Value):
        return True


class EqOperator(BaseOperator):
    name = "eq"

    def apply(self, a, b):
        return a == b
    
class NeqOperator(BaseOperator):
    name = "neq"

    def apply(self, a, b):
        return a != b


class GtOperator(BaseOperator):
    name = "gt"

    def apply(self, a, b):
        return a > b


class GteOperator(BaseOperator):
    name = "gte"

    def apply(self, a, b):
        return a >= b


class LtOperator(BaseOperator):
    name = "lt"

    def apply(self, a, b):
        return a < b


class LteOperator(BaseOperator):
    name = "lte"

    def apply(self, a, b):
        return a <= b


class InOperator(BaseOperator):
    name = "in"

    def apply(self, a, b):
        return a in b
    
class NinOperator(BaseOperator):
    name = "nin"

    def apply(self, a, b):
        return a not in b


class ContainsOperator(BaseOperator):
    name = "contains"

    def apply(self, a, b):
        return b in a

@dataclass
class QueryExpression:
    target: str
    field: str
    operator: BaseOperator
    value: any

    def match(self, obj):
        return self.operator.apply(getattr(obj, self.field), self.value)


class OperatorRegistry:
    _ops = {}

    @classmethod
    def register(cls, operator: BaseOperator):
        cls._ops[operator.name] = operator

    @classmethod
    def get(cls, name: str) -> BaseOperator:
        if name not in cls._ops:
            raise ValueError(f"Unknown operator: {name}")

        return cls._ops[name]


OperatorRegistry.register(EqOperator())
OperatorRegistry.register(NeqOperator())
OperatorRegistry.register(LtOperator())
OperatorRegistry.register(LteOperator())
OperatorRegistry.register(GtOperator())
OperatorRegistry.register(GteOperator())
OperatorRegistry.register(InOperator())
OperatorRegistry.register(ContainsOperator())


class ExpressionParser:
    def __init__(self):
        self.registry = OperatorRegistry

    def parse(self, key: str, value):
        parts = key.split("__")

        op_name = "eq"

        if len(parts) == 2:
            target, field = parts
        elif len(parts) == 3:
            target, field, op_name = parts
        else:
            raise ValueError(f"Invalid expression: {key}")
        
        self.validate_target(target)
        
        operator = self.registry.get(op_name)
        operator.validate(value)

        return QueryExpression(target, field, operator, value)
    
    def validate_target(self, target):
        allowed = {
            "images",
            "annotations",
            "categories"
        }

        if target not in allowed:
            raise ValueError(f"Invalid target: {target}")
