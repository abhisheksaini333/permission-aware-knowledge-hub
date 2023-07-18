import hashlib
from pathlib import Path


def verify_file(path, item):
    path = Path(path)
    if not path.exists() or path.stat().st_size != item["bytes"]:
        return False
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest() == item["sha256"]


def target_path(root, item):
    root = Path(root).resolve()
    name = item["model"].split("/")[-1]
    if "/" in item["file"] or "\\" in item["file"] or item["file"] in {".", ".."}:
        raise ValueError("Invalid artifact filename")
    target = (root / name / item["file"]).resolve()
    if root not in target.parents:
        raise ValueError("Artifact escapes cache directory")
    return target
