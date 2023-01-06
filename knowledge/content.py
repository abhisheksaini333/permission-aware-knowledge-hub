import hashlib

def normalize(payload):
 try:text=payload.decode("utf-8-sig").replace("\r\n","\n").replace("\r","\n")
 except UnicodeDecodeError as exc:raise ValueError("Document must be UTF-8") from exc
 if "\0" in text:raise ValueError("Document contains null bytes")
 if not text.strip():raise ValueError("Document is empty")
 return text

def content_digest(text):return hashlib.sha256(text.encode()).hexdigest()
def document_key(tenant,source):return content_digest(tenant+"\0"+source)[:32]
