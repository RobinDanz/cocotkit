from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class COCOImage:
    id: int = 0
    file_name: str = ""
    height: int = 0
    width: int = 0
    
@dataclass
class COCOAnnotation:
    id: int = 0
    is_crowd: int = 0
    area: int = 0
    image_id: int = 0
    category_id: int = 0
    bbox: Tuple[int, int, int, int] = [0, 0, 0, 0]
    segmentation: List
    
@dataclass
class COCOCategory:
    id: int = 0
    name: str = ""
    
    
    