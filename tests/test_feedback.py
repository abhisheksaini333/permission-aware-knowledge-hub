from knowledge.store import Store
import pytest

def test_feedback_validates_rating_and_preserves_tenant():
 s=Store();key=s.feedback("a","u","qhash","helpful","A useful source")
 assert s.feedback_records("a")[0]["id"]==key
 assert s.feedback_records("b")==[]
 with pytest.raises(ValueError):s.feedback("a","u","q","nonsense","")
