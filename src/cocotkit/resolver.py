class MetadataResolver:
    def __init__(self, pattern: str):
        self.pattern = pattern

    def resolve(self, dataset):
        return self.pattern.format(**dataset.meta)