from langchain import LLMChain,PromptTemplate
from langchain.llms.base import LLM

class LocalLLM(LLM):
 def __init__(self,generator):self.generator=generator
 def __call__(self,prompt,stop=None):
  answer=self.generator.generate(prompt)
  for marker in stop or []:answer=answer.split(marker,1)[0]
  return answer
 @property
 def _identifying_params(self):return {"backend":"local-flan-t5"}

class GroundedChain:
 def __init__(self,generator):
  self.llm=LocalLLM(generator)
  self.chain=LLMChain(prompt=PromptTemplate(input_variables=["grounded_prompt"],template="{grounded_prompt}"),llm=self.llm)
 def generate(self,prompt):return self.chain.run(prompt)
