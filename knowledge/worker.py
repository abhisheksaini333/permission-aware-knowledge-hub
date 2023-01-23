import uuid
from .chunks import chunk_text

class IndexWorker:
 def __init__(self,store,encoder=None,size=700,overlap=100):
  self.store=store;self.encoder=encoder;self.size=size;self.overlap=overlap;self.owner=str(uuid.uuid4())
 def once(self):
  job=self.store.claim(self.owner)
  if not job:return False
  try:
   doc=self.store.document(job["document_id"])
   if not doc or doc["deleted"] or doc["revision"]!=job["revision"]:
    self.store.finish(job);return True
   chunks=[];offset=0
   for page,text in enumerate(doc["content"].split("\f"),1):
    for c in chunk_text(text,self.size,self.overlap,page):
     c["document_start"]=offset+c["start"];c["document_end"]=offset+c["end"];chunks.append(c)
    offset+=len(text)+1
   if self.encoder:
    vectors=self.encoder.encode([c["text"] for c in chunks])
    for c,v in zip(chunks,vectors):c["vector"]=v
   self.store.index(doc["id"],job["revision"],chunks)
   self.store.finish(job)
  except Exception as exc:self.store.finish(job,type(exc).__name__)
  return True
