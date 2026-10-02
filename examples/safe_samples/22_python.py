from pathlib import Path
def read_file(name):
    root = Path("/srv/files").resolve()
    target = (root / name).resolve()
    if target.is_relative_to(root): return target.read_text()
    raise ValueError("invalid path")
