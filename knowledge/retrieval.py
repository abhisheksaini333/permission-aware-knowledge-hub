import re,math
from collections import Counter

def tokens(text):return re.findall(r"[^\W_]+",text.lower())

def lexical(query,chunks):
 terms=set(tokens(query));docs=[Counter(tokens(c["text"])) for c in chunks]
 if not docs or not terms:return []
 avg=sum(sum(d.values()) for d in docs)/len(docs) or 1
 freq={t:sum(t in d for d in docs) for t in terms}
 out=[]
 for chunk,d in zip(chunks,docs):
  score=0.;length=sum(d.values())
  for t in terms:
   if d[t]:
    idf=math.log(1+(len(docs)-freq[t]+.5)/(freq[t]+.5))
    score+=idf*d[t]*2.5/(d[t]+1.5*(.25+.75*length/avg))
  if score:out.append((chunk,score))
 return sorted(out,key=lambda x:(-x[1],x[0]["id"]))
