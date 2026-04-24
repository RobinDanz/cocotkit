import json
from typing import Dict, Any

from pathlib import Path

class COCOReader:
    def __init__(self):
        pass
    
    @classmethod
    def read(cls, file: str | Path) -> Dict[str, Any]:
        with open(file=file) as f:
            data = json.load(f)
            
            return data