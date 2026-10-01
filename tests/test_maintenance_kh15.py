import hashlib
import pytest
from knowledge.artifacts import target_path, verify_file

def test_artifact_rejects_empty_filename(tmp_path):
    with pytest.raises(ValueError): target_path(tmp_path,{"model":"owner/model","file":""})

def test_artifact_rejects_symlink(tmp_path):
    original=tmp_path/"original"; original.write_bytes(b"model")
    link=tmp_path/"link"; link.symlink_to(original)
    item={"bytes":5,"sha256":hashlib.sha256(b"model").hexdigest()}
    assert not verify_file(link,item)
    assert not verify_file(tmp_path,item)
    assert verify_file(original,item)
