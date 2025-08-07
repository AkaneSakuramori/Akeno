import os
from pathlib import Path

class FontManager:
    def __init__(self, directory):
        self.dir = Path(directory)
        self.dir.mkdir(exist_ok=True)
        self.mapping = {}  # .ass font -> actual filename

    def load_fonts(self):
        for f in self.dir.glob('*.[ot]tf'):
            name = f.stem.lower()
            self.mapping[name] = str(f)
        return self.mapping

    def get_font_path(self, font_name):
        key = font_name.strip().lower()
        return self.mapping.get(key)

    def add_font(self, file_stream, filename):
        path = self.dir / filename
        with open(path, 'wb') as f:
            f.write(file_stream.read())
        self.load_fonts()
        return path


---
