import threading
import numpy as np

def mean_pool(hidden,mask):
 weights=mask[...,None];pooled=(hidden*weights).sum(axis=1)/np.maximum(weights.sum(axis=1),1)
 return pooled/np.maximum(np.linalg.norm(pooled,axis=1,keepdims=True),1e-9)

class MiniLMEncoder:
 def __init__(self,path):
  import torch
  from transformers import AutoTokenizer,AutoModel
  torch.set_num_threads(2)
  self.tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True)
  self.model=AutoModel.from_pretrained(path,local_files_only=True).eval();self.lock=threading.Lock()
 def encode(self,texts):
  import torch
  result=[]
  with self.lock,torch.no_grad():
   for i in range(0,len(texts),16):
    batch=self.tokenizer(texts[i:i+16],padding=True,truncation=True,max_length=256,return_tensors="pt")
    hidden=self.model(**batch).last_hidden_state.cpu().numpy()
    result.extend(mean_pool(hidden,batch["attention_mask"].cpu().numpy()).tolist())
  return result
