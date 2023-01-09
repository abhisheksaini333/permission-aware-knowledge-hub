import pytest
from knowledge.chunks import chunk_text

def test_offsets_reconstruct_source_and_cover_tail():
 text="abcdefghij"*31
 chunks=chunk_text(text,size=80,overlap=10)
 assert chunks[0]["start"]==0 and chunks[-1]["end"]==len(text)
 for c in chunks:assert text[c["start"]:c["end"]]==c["text"]
 assert chunks[1]["start"]==70

def test_empty_and_bad_limits():
 assert chunk_text("")==[]
 with pytest.raises(ValueError):chunk_text("x",size=5,overlap=5)
