from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from docx import Document
import fitz, jwt, io, os
from .data import ROLES
from .services import token, profile_from_text, match, roadmap, guidance, evaluate
from .rag import rag
app=FastAPI(title='Career IQ API',version='1.0'); app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*']); security=HTTPBearer(); users={}; profiles={}; progress={}
def current(c:HTTPAuthorizationCredentials=Depends(security)):
 try:return jwt.decode(c.credentials,os.getenv('JWT_SECRET_KEY','dev-career-iq-secret'),algorithms=['HS256'])['sub']
 except: raise HTTPException(401,'Invalid or expired session')
class Auth(BaseModel): email:EmailStr; password:str; name:str='Student'
class Chat(BaseModel): question:str
class RoadmapUpdate(BaseModel): role_id:str; item_id:str; completed:bool
class InterviewStart(BaseModel): role_id:str; difficulty:str='Intermediate'; kind:str='Technical'
class Answer(BaseModel): answer:str
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/auth/signup')
def signup(a:Auth):
 if a.email in users: raise HTTPException(409,'Account already exists')
 users[a.email]={'name':a.name,'password':a.password}; return {'token':token(a.email),'user':{'email':a.email,'name':a.name}}
@app.post('/auth/login')
def login(a:Auth):
 if a.email not in users or users[a.email]['password']!=a.password: raise HTTPException(401,'Incorrect email or password')
 return {'token':token(a.email),'user':{'email':a.email,'name':users[a.email]['name']}}
@app.get('/jobs')
def jobs(): return ROLES
@app.post('/resume/analyze')
async def resume(file:UploadFile=File(...),email:str=Depends(current)):
 if not file.filename.lower().endswith(('.pdf','.docx','.txt')): raise HTTPException(400,'Upload a PDF, DOCX, or TXT resume.')
 data=await file.read()
 try:
  if file.filename.lower().endswith('.pdf'): text=''.join(p.get_text() for p in fitz.open(stream=data,filetype='pdf'))
  elif file.filename.lower().endswith('.docx'): text='\n'.join(x.text for x in Document(io.BytesIO(data)).paragraphs)
  else: text=data.decode('utf-8',errors='ignore')
 except Exception: raise HTTPException(422,'We could not read this file. Try exporting it again.')
 if len(text.strip())<40: raise HTTPException(422,'The resume did not contain enough readable text.')
 p=profile_from_text(text); p['raw_text']=text; profiles[email]=p; return {**p,'matches':match(p)}
@app.get('/users/me')
def me(email:str=Depends(current)):
 p=profiles.get(email,{'name':users.get(email,{}).get('name','Student'),'all_skills':[],'skills':{},'resume_score':0}); m=match(p) if p.get('all_skills') else []; return {'profile':p,'matches':m,'progress':progress.get(email,{})}
@app.get('/jobs/matches')
def matches(email:str=Depends(current)):
 if email not in profiles: raise HTTPException(404,'Analyze your resume before matching roles.')
 return match(profiles[email])
@app.get('/skills/gap/{role_id}')
def gap(role_id:str,email:str=Depends(current)):
 if email not in profiles: raise HTTPException(404,'Analyze your resume first.')
 return next((x for x in match(profiles[email]) if x['id']==role_id),None)
@app.get('/roadmap/{role_id}')
def get_roadmap(role_id:str,email:str=Depends(current)): return roadmap(role_id,profiles.get(email,{}).get('all_skills',[]))
@app.post('/roadmap/progress')
def update_roadmap(x:RoadmapUpdate,email:str=Depends(current)): progress.setdefault(email,{})[x.item_id]=x.completed; return progress[email]
@app.post('/chat')
def chat(x:Chat,email:str=Depends(current)):
 p=profiles.get(email,{}); m=match(p) if email in profiles else []
 context='\n'.join(rag.retrieve(x.question)); key=os.getenv('GEMINI_API_KEY')
 if key:
  try:
   from google import genai
   prompt=f"You are a concise career mentor. Profile: skills={p.get('all_skills',[])}. Top match={m[0]['title'] if m else 'unknown'}. Retrieved context: {context}. Question: {x.question}"
   answer=genai.Client(api_key=key).models.generate_content(model='gemini-2.0-flash',contents=prompt).text
   if answer: return {'answer':answer,'source':'gemini+rag'}
  except Exception: pass
 return {'answer':guidance(x.question,p,m)+"\n\nGrounding: "+context,'source':'local-rag-fallback'}
@app.post('/interview/start')
def start(x:InterviewStart,email:str=Depends(current)):
 role=next((r for r in ROLES if r['id']==x.role_id),ROLES[0]); return {'question':f"Tell me about a project where you used {role['required'][0]}. What was the problem, your approach, and measurable result?",'role':role['title'],'difficulty':x.difficulty}
@app.post('/interview/evaluate')
def interview(x:Answer,email:str=Depends(current)):
 if len(x.answer.strip())<15: raise HTTPException(400,'Please provide a more complete answer.')
 result=evaluate(x.answer); progress.setdefault(email,{})['last_interview']=result; return result
@app.get('/analytics')
def analytics(email:str=Depends(current)):
 p=profiles.get(email,{}); m=match(p) if p else []; last=progress.get(email,{}).get('last_interview',{}); return {'career_score':round((p.get('resume_score',0)+(m[0]['score'] if m else 0)*1.2+last.get('overall',0)*10)/3.2),'skill_count':len(p.get('all_skills',[])),'interview':last,'match_scores':[{'name':x['title'],'score':x['score']} for x in m[:4]]}
