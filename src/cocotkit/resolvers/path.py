from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cocotkit.coco import COCODataset, COCOImage

import os
from collections import defaultdict

class ImagePathResolver:
    def __init__(
            self,
            root: str,
            use_cache: bool = True,
            scan_depth: int = 2,
    ):
        self.root = root
        self.use_cache = use_cache
        self.scan_depth = scan_depth

        self._index = None

    def resolve(self, dataset: COCODataset, image: COCOImage):
        fname = image.file_name

        if os.path.isabs(fname)  and os.path.exists(fname):
            return fname
        
        candidate = os.path.join(self.root, fname)
        if os.path.exists(candidate):
            return candidate
        
        source = dataset.meta.get("source")
        if source:
            candidate = os.path.join(self.root, source, fname)

            if os.path.exists(candidate):
                return candidate
            
        if self.use_cache:
            return self._resolve_with_index(fname)
        
        raise FileNotFoundError(f"Image not found: {fname}")
    
    def _resolve_with_index(self, fname: str):
        if self._index is None:
            self._build_index()

        matches = self._index.get(os.path.basename(fname))

        if not matches:
            raise FileNotFoundError(f"Image not found in index: {fname}")
        
        if len(matches) > 1:
            return matches[0]
        
        return matches[0]
        
    def _build_index(self):
        self._index = defaultdict(list)

        for root, dirs, files in os.walk(self.root):
            depth = root[len(self.root):].count(os.sep)

            if depth > self.scan_depth:
                continue

            for f in files:
                self._index[f].append(os.path.join(root, f))