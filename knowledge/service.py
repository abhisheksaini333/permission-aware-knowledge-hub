from .identity import allowed
from .retrieval import lexical,dense,fuse,rerank

class KnowledgeHub:
 def __init__(self,store,encoder=None,generator=None):
  self.store=store;self.encoder=encoder;self.generator=generator
 def visible_chunks(self,principal):
  principal=self.store.resolve(principal)
  return [c for c in self.store.chunks(principal.tenant) if allowed(principal,principal.tenant,self.store.document(c["document_id"])["groups"])]
 def search(self,principal,query,mode="lexical",limit=5):
  if not query.strip() or len(query)>1000:raise ValueError("Enter a question between 1 and 1000 characters")
  if mode not in {"lexical","dense","fusion","rerank"}:raise ValueError("Unknown retrieval mode")
  if not 1<=limit<=20:raise ValueError("Limit must be between 1 and 20")
  chunks=self.visible_chunks(principal)
  lex=lexical(query,chunks)
  if mode=="lexical":ranking=lex
  else:
   if not self.encoder:raise ValueError("Dense model is unavailable")
   vec=dense(self.encoder.encode([query])[0],chunks)
   ranking=vec if mode=="dense" else fuse(lex,vec)
   if mode=="rerank":ranking=rerank(query,ranking)
  return [dict(c,score=score,title=self.store.document(c["document_id"])["title"],source=self.store.document(c["document_id"])["source"]) for c,score in ranking[:limit]]

 def ask(self,principal,question,mode="lexical"):
  from .answers import build_prompt,citations,supported
  hits=self.search(principal,question,mode,limit=3)
  prompt,used=build_prompt(question,hits)
  if not used or not self.generator:return dict(answer="No supported answer is available.",abstained=True,citations=[],cached=False)
  answer=self.generator.generate(prompt).strip()
  valid={c["id"] for c in self.visible_chunks(principal)}
  if any(h["id"] not in valid for h in used):return dict(answer="Evidence changed while answering. Please try again.",abstained=True,citations=[],cached=False)
  if not supported(answer,used):return dict(answer="The available evidence does not support a reliable answer.",abstained=True,citations=[],cached=False)
  return dict(answer=answer,abstained=False,citations=citations(used),cached=False)
