import threading,time
from collections import defaultdict,deque

class RateLimiter:
 def __init__(self,limit=120,window=60):
  self.limit=limit;self.window=window;self.events=defaultdict(deque);self.lock=threading.Lock()
 def allow(self,key,now=None):
  now=time.monotonic() if now is None else now
  with self.lock:
   q=self.events[key]
   while q and q[0]<=now-self.window:q.popleft()
   if len(q)>=self.limit:return False
   q.append(now)
   if len(self.events)>10000:
    self.events={k:v for k,v in self.events.items() if v and v[-1]>now-self.window}
    self.events=defaultdict(deque,self.events)
   return True
