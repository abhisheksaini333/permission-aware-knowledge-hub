import hashlib
import pytest
from knowledge.artifacts import verify_file,target_path

def test_artifact_hash_and_size_must_match(tmp_path):
 p=tmp_path/"model.bin";p.write_bytes(b"model")
 item=dict(bytes=5,sha256=hashlib.sha256(b"model").hexdigest())
 assert verify_file(p,item)
 p.write_bytes(b"other");assert not verify_file(p,item)
 with pytest.raises(ValueError):target_path(tmp_path,{"model":"owner/model","file":"../secret"})
