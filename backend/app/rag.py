"""Small, dependency-tolerant RAG adapter. FAISS is used when installed."""
from .services import KB
class CareerRAG:
 def __init__(self):
  self.docs=KB; self.model=None; self.index=None
  try:
   from sentence_transformers import SentenceTransformer
   import faiss
   self.model=SentenceTransformer('all-MiniLM-L6-v2'); vectors=self.model.encode(self.docs,normalize_embeddings=True); self.index=faiss.IndexFlatIP(vectors.shape[1]); self.index.add(vectors)
  except Exception: pass
 def retrieve(self,query,k=2):
  if self.index:
   _, ids=self.index.search(self.model.encode([query],normalize_embeddings=True),k); return [self.docs[i] for i in ids[0]]
  terms=set(query.lower().split()); return sorted(self.docs,key=lambda x:len(terms&set(x.lower().split())),reverse=True)[:k]
rag=CareerRAG()
