from fastapi import FastAPI,Depends,HTTPException,Header
from pydantic import BaseModel,constr

class AskRequest(BaseModel):
 question: constr(min_length=1,max_length=1000)
 mode: str = "lexical"

from .auth import AuthError,OIDCVerifier
from .identity import allowed
from .settings import Settings

def create_app(hub,verifier=None):
 settings=Settings.from_env();verifier=verifier or OIDCVerifier(settings.issuer,settings.audience)
 app=FastAPI(title="Permission-aware Knowledge Hub",version="0.1.0")
 app.state.hub=hub
 def principal(authorization: str = Header(default="")):
  if not authorization.startswith("Bearer "):raise HTTPException(401,"Sign in to continue",headers={"WWW-Authenticate":"Bearer"})
  try:return hub.store.resolve(verifier.verify(authorization[7:]))
  except AuthError:raise HTTPException(401,"Session expired or invalid",headers={"WWW-Authenticate":"Bearer"})
 def admin(p=Depends(principal)):
  if not p.is_admin:raise HTTPException(403,"Administrator access required")
  return p
 @app.get("/health")
 def health():return {"status":"ok"}
 @app.get("/api/me")
 def me(p=Depends(principal)):return dict(subject=p.subject,tenant=p.tenant,groups=sorted(p.groups),roles=sorted(p.roles))
 @app.get("/api/search")
 def search(q:str,mode:str="lexical",limit:int=5,p=Depends(principal)):
  try:return {"hits":hub.search(p,q,mode,limit)}
  except ValueError as exc:raise HTTPException(422,str(exc))
 @app.post("/api/ask")
 def ask(body:AskRequest,p=Depends(principal)):
  try:return hub.ask(p,body.question,body.mode)
  except ValueError as exc:raise HTTPException(422,str(exc))
  except RuntimeError:raise HTTPException(503,"Answer model is temporarily unavailable. Search sources or try again.")
 @app.get("/api/documents")
 def documents(p=Depends(principal)):
  docs=hub.store.documents(p.tenant)
  return {"documents":[{k:v for k,v in d.items() if k!="content"} for d in docs if p.is_admin or (not d["deleted"] and allowed(p,d["tenant"],d["groups"]))]}
 return app
