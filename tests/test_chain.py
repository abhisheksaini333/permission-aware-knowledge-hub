from knowledge.chain import GroundedChain

class Echo:
 def generate(self,prompt):return prompt

def test_chain_preserves_grounded_prompt_and_stop_boundary():
 chain=GroundedChain(Echo())
 assert chain.generate("Evidence: hello\nQuestion: greeting?")=="Evidence: hello\nQuestion: greeting?"
 assert chain.llm("one STOP two",stop=["STOP"])=="one "
