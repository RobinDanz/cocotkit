import importlib
import pkgutil
from typing import Type

from cocotkit.cli.commands import BaseCommand


def discover_commands() -> list[Type[BaseCommand]]:
    commands = []

    package = "cocotkit.cli.commands"
    module = importlib.import_module(package)

    for _, name, _ in pkgutil.iter_modules(module.__path__):
        mod = importlib.import_module(f"{package}.{name}")

        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, BaseCommand) and obj is not BaseCommand:
                commands.append(obj)

    return commands
