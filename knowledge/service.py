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
   query_vector=self.encoder.encode([query])[0]
   vec=self.store.vector_search(principal,query_vector,20) if hasattr(self.store,"vector_search") else dense(query_vector,chunks)
   ranking=vec if mode=="dense" else fuse(lex,vec)
   if mode=="rerank":ranking=rerank(query,ranking)
  valid={c["id"] for c in self.visible_chunks(principal)}
  return [dict(c,score=score,title=self.store.document(c["document_id"])["title"],source=self.store.document(c["document_id"])["source"]) for c,score in ranking if c["id"] in valid][:limit]

 def ask(self,principal,question,mode="lexical"):
  from .answers import build_prompt,citations,supported
  import json
  from .content import content_digest
  effective=self.store.resolve(principal)
  signature=dict(subject=principal.subject,groups=sorted(effective.groups),roles=sorted(effective.roles),chunks=[c["id"] for c in self.visible_chunks(principal)],question=question,mode=mode)
  cache_key=content_digest(json.dumps(signature,sort_keys=True))
  cached=self.store.cache_get(principal.tenant,cache_key)
  if cached:
   p=self.store.resolve(principal)
   valid=True
   for cite in cached["citations"]:
    d=self.store.document(cite["document_id"])
    if not d or d["deleted"] or d["revision"]!=cite["revision"] or not allowed(p,d["tenant"],d["groups"]):valid=False
   if valid:return dict(cached,cached=True)
  hits=self.search(principal,question,mode,limit=3)
  prompt,used=build_prompt(question,hits)
  if not used or not self.generator:return dict(answer="No supported answer is available.",abstained=True,citations=[],cached=False)
  answer=self.generator.generate(prompt).strip()
  valid={c["id"] for c in self.visible_chunks(principal)}
  if any(h["id"] not in valid for h in used):return dict(answer="Evidence changed while answering. Please try again.",abstained=True,citations=[],cached=False)
  if not supported(answer,used):return dict(answer="The available evidence does not support a reliable answer.",abstained=True,citations=[],cached=False)
  result=dict(answer=answer,abstained=False,citations=citations(used),cached=False)
  self.store.cache_put(principal.tenant,cache_key,result)
  return result
