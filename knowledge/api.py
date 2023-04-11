from fastapi import FastAPI,Depends,HTTPException,Header,UploadFile,File,Form,Response
from pydantic import BaseModel,constr,conlist

class AccessRequest(BaseModel):
 groups: conlist(constr(min_length=1,max_length=80),max_items=30)

class FeedbackRequest(BaseModel):
 question: constr(min_length=1,max_length=1000)
 rating: constr(regex="^(helpful|incorrect|missing_source)$")
 comment: constr(max_length=1000) = ""

class MembershipRequest(BaseModel):
 groups: conlist(constr(min_length=1,max_length=80),max_items=30)
 roles: conlist(constr(regex="^(reader|admin)$"),max_items=2)

class DocumentRequest(BaseModel):
 source: constr(min_length=1,max_length=240)
 title: constr(min_length=1,max_length=200)
 content: constr(min_length=1,max_length=1000000)
 groups: conlist(constr(min_length=1,max_length=80),max_items=30) = []

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
 from .limits import RateLimiter
 limiter=RateLimiter()
 @app.middleware("http")
 async def security_headers(request,call_next):
  response=await call_next(request)
  response.headers["X-Content-Type-Options"]="nosniff"
  response.headers["X-Frame-Options"]="DENY"
  response.headers["Referrer-Policy"]="same-origin"
  response.headers["Cache-Control"]="no-store"
  return response
 def principal(authorization: str = Header(default="")):
  if not authorization.startswith("Bearer "):raise HTTPException(401,"Sign in to continue",headers={"WWW-Authenticate":"Bearer"})
  try:p=hub.store.resolve(verifier.verify(authorization[7:]))
  except AuthError:raise HTTPException(401,"Session expired or invalid",headers={"WWW-Authenticate":"Bearer"})
  if not {"reader","admin"}.intersection(p.roles):raise HTTPException(403,"Application access has been revoked")
  if not limiter.allow((p.tenant,p.subject)):raise HTTPException(429,"Too many requests; try again shortly",headers={"Retry-After":"60"})
  try:return p
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
 @app.get("/api/documents/{key}/revisions/{revision}")
 def revision(key:str,revision:int,p=Depends(principal)):
  current=hub.store.document(key);old=hub.store.revision(key,revision)
  if not current or current["deleted"] or not old or not allowed(p,current["tenant"],current["groups"]) or not allowed(p,old["tenant"],old["groups"]):raise HTTPException(404,"Source unavailable")
  return old
 @app.post("/api/documents",status_code=201)
 def ingest(body:DocumentRequest,p=Depends(admin)):
  from .content import normalize
  try:content=normalize(body.content.encode())
  except ValueError as exc:raise HTTPException(422,str(exc))
  return hub.store.ingest(p.tenant,body.source,body.title,content,body.groups)
 @app.post("/api/upload",status_code=201)
 async def upload(file:UploadFile=File(...),groups:str=Form(""),title:str=Form(""),p=Depends(admin)):
  from .formats import extract
  payload=await file.read(settings.max_document_bytes+1)
  try:
   content=extract(file.filename or "",payload,settings.max_document_bytes)
   body=DocumentRequest(source=file.filename or "",title=title or file.filename,content=content,groups=[g.strip() for g in groups.split(",") if g.strip()])
  except ValueError as exc:raise HTTPException(422,str(exc))
  return hub.store.ingest(p.tenant,body.source,body.title,body.content,body.groups)
 @app.delete("/api/documents/{key}",status_code=204)
 def delete(key:str,p=Depends(admin)):
  if not hub.store.delete(key,p.tenant):raise HTTPException(404,"Document not found")
  hub.store.audit(p.tenant,p.subject,"document.deleted",{"document_id":key})
  return Response(status_code=204)
 @app.put("/api/memberships/{subject}")
 def membership(subject:str,body:MembershipRequest,p=Depends(admin)):
  if not 1<=len(subject)<=200:raise HTTPException(422,"Invalid subject")
  hub.store.set_membership(p.tenant,subject,body.groups,body.roles)
  hub.store.audit(p.tenant,p.subject,"membership.changed",{"subject":subject})
  return {"status":"updated"}
 @app.get("/api/jobs")
 def jobs(p=Depends(admin)):return {"jobs":hub.store.jobs(p.tenant)}
 @app.post("/api/feedback",status_code=201)
 def feedback(body:FeedbackRequest,p=Depends(principal)):
  from .content import content_digest
  return {"id":hub.store.feedback(p.tenant,p.subject,content_digest(body.question),body.rating,body.comment)}
 @app.post("/api/documents/{key}/reindex",status_code=202)
 def reindex(key:str,p=Depends(admin)):
  if not hub.store.reindex(key,p.tenant):raise HTTPException(404,"Document unavailable")
  return {"status":"pending"}
 @app.put("/api/documents/{key}/access")
 def access(key:str,body:AccessRequest,p=Depends(admin)):
  d=hub.store.document(key)
  if not d or d["tenant"]!=p.tenant or d["deleted"]:raise HTTPException(404,"Document unavailable")
  return hub.store.ingest(p.tenant,d["source"],d["title"],d["content"],body.groups)
 @app.get("/api/audit")
 def audit(p=Depends(admin)):return {"events":hub.store.audit_events(p.tenant)}
 @app.get("/api/config")
 def config():return dict(issuer=settings.issuer,client_id="knowledge-ui",dense_available=hub.encoder is not None,answers_available=hub.generator is not None)
 return app
