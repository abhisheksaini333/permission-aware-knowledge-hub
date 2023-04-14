from knowledge.runtime import build_hub

def test_runtime_without_models_remains_explicitly_lexical(tmp_path):
 hub=build_hub("sqlite:///"+str(tmp_path/"hub.db"))
 assert hub.encoder is None and hub.generator is None
 assert hub.store.documents("acme")==[]
