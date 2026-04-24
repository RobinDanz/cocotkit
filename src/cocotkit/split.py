from typing import Dict, List, Any


class COCOSplitter:
    def __init__(self):
        pass
    
    def split(self, data: Dict[str, Any]):
        images = data["images"]
        categories = data["categories"]
        annotations = data["annotations"]
        
        for image in images:
            id = image["id"]
            file_name = image["file_name"]

            related_annotations = [ann for ann in annotations if ann["image_id"] == id]
            
    def get_related(
        self, 
        annotations: List[Dict[str, Any]], 
        categories: List[Dict[str, Any]], 
        image_id: int
    ):
        related_annotations = []
        related_categories = []
        for ann in annotations:
            category_id = ann["category_id"]
            related_annotations.append(ann)
            
            