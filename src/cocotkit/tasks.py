from __future__ import annotations
import threading
from typing import TYPE_CHECKING, List, Tuple

import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image


from cocotkit.resolvers.path import ImagePathResolver
from cocotkit.draw import PILDrawer

if TYPE_CHECKING:
    from cocotkit.coco import COCODataset

class Task:
    def run(self, data):
        raise NotImplementedError
    

class ImageCopyTask(Task):
    def __init__(
        self,
        images_root: str,
        output_root: str,
        split_key: str = "split",
        mode: str = "copy",
        workers: int = 8,
        resolver = None
    ):
        
        self.resolver = ImagePathResolver(images_root)
        self.output_root = output_root
        self.split_key = split_key
        self.mode = mode
        self.workers = workers

        if mode == "copy":
            self.op = shutil.copy2
        elif mode == "move":
            self.op = shutil.move
        elif mode == "symlink":
            self.op = os.symlink
        else:
            raise ValueError(f"Unknow mode: {mode}")
        
    def run(self, datasets: List[COCODataset]):
        os.makedirs(self.output_root, exist_ok=True)

        tasks = self._build_tasks(datasets=datasets)
        tasks = self._deduplicate(tasks)

        self._execute(tasks)

    def _build_tasks(self, datasets: List[COCODataset]) -> List[Tuple[str, str]]:
        tasks = []

        for ds in datasets:
            split = ds.meta.get(self.split_key, "default")

            for img in ds.images:
                src = self.resolver.resolve(ds, img)
                dst = os.path.join(self.output_root, split, img.file_name)

                tasks.append((src, dst))
        
        return tasks

    def _deduplicate(self, tasks: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        return list(set(tasks))
    
    def _execute(self, tasks: List[Tuple[str, str]]):
        total = len(tasks)
        completed = 0
        lock = threading.Lock()

        def process(task: Tuple[str, str]):
            src, dst = task
            print("======================")
            print(src)
            print(dst)

            if not os.path.exists(src):
                return
            
            os.makedirs(os.path.dirname(dst), exist_ok=True)

            if not os.path.exists(dst):
                self.op(src, dst)

            return f"ok: {src}"

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(process, t) for t in tasks]

            for future in as_completed(futures):
                try:
                    result = future.result()
                except Exception as e:
                    print(f"[ERROR] {e}")

                with lock:
                    completed += 1
                    if completed % 100 == 0 or completed == total:
                        print(f"[PROGRESS] {completed}/{total}")

class DrawTask(Task):
    def __init__(
        self,
        images_root: str,
        output_root: str,
        resolver = None,
        drawer = None,
        workers = 8
    ):
        self.resolver = resolver or ImagePathResolver(images_root)
        self.drawer = drawer or PILDrawer()
        self.output_root = output_root
        self.workers = workers

    
    def run(self, datasets: List[COCODataset]):
        os.makedirs(self.output_root, exist_ok=True)

        tasks = self._build_tasks(datasets)
        self._execute(tasks)

    def _build_tasks(self, datasets: List[COCODataset]):
        tasks = []

        for ds in datasets:
            split = ds.meta.get("split", "default")

            ann_map = {}

            for ann in ds.annotations:
                ann_map.setdefault(
                    ann.image_id,
                    []
                ).append(ann)

            for img in ds.images:
                src = self.resolver.resolve(ds, img)

                dst = os.path.join(
                    self.output_root,
                    split,
                    img.file_name
                )

                anns = ann_map.get(img.id, [])

                tasks.append(
                    (
                        src,
                        dst,
                        anns,
                        ds.categories
                    )
                )
        return tasks
    
    def _execute(self, tasks):
        total = len(tasks)
        completed = 0

        lock = threading.Lock()

        def process(task):
            src, dst, anns, categories = task

            os.makedirs(
                os.path.dirname(dst),
                exist_ok=True
            )

            image = Image.open(src).convert("RGB")

            image = self.drawer.draw(
                image=image,
                annotations=anns,
                categories=categories
            )

            image.save(dst)

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [
                executor.submit(process, t)
                for t in tasks
            ]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"[ERROR] {e}")

                with lock:
                    completed += 1

                    if (
                        completed % 100 == 0
                        or completed == total
                    ):
                        print(
                            f"[PROGRESS] {completed}/{total}"
                        )