import pytest
from knowledge.answers import build_prompt

def test_complete_prompt_budget():
    fixed, _ = build_prompt("Question", [], 1000)
    with pytest.raises(ValueError): build_prompt("Question", [], len(fixed)-1)
    hits = [{"text": "a"*10}, {"text": "b"*20}]
    prompt, used = build_prompt("Question", hits, len(fixed)+14)
    assert len(prompt) <= len(fixed)+14
    assert len(used) == 1
    assert build_prompt("Question", [], len(fixed))[0] == fixed
