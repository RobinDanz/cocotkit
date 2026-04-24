from abc import ABC, abstractmethod
import argparse

class BaseCommand(ABC):
    name: str
    help: str
    
    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        pass
    
    @abstractmethod
    def run(self, args: argparse.Namespace) -> None:
        pass
    