from collections import Counter
from .retrieval import tokens

def retrieval_metrics(hits,expected):
 if expected is None:return {"recall_at_3":None,"reciprocal_rank":None}
 ranks=[i for i,h in enumerate(hits[:3],1) if h["source"]==expected]
 return {"recall_at_3":float(bool(ranks)),"reciprocal_rank":1/ranks[0] if ranks else 0.}

def answer_metrics(answer,abstained,expected):
 if expected is None:return {"exact_match":None,"token_f1":None,"correct_abstention":float(abstained)}
 a=tokens(answer) if not abstained else [];b=tokens(expected);shared=sum((Counter(a)&Counter(b)).values())
 precision=shared/len(a) if a else 0;recall=shared/len(b) if b else 0
 return {"exact_match":float(a==b),"token_f1":2*precision*recall/(precision+recall) if precision+recall else 0.,"correct_abstention":None}

def average(rows,key):
 values=[r[key] for r in rows if r.get(key) is not None]
 return sum(values)/len(values) if values else None
