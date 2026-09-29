import re, os, jwt
from datetime import datetime, timedelta, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .data import ROLES, SKILLS, RESOURCES
SECRET=os.getenv('JWT_SECRET_KEY','dev-career-iq-secret')
def token(email): return jwt.encode({'sub':email,'exp':datetime.now(timezone.utc)+timedelta(days=7)},SECRET,algorithm='HS256')
def extract_skills(text):
 t=' '+text.lower().replace('-',' ')+' '; out={}
 for group, values in SKILLS.items():
  hits=[s for s in values if re.search(r'(?<!\\w)'+re.escape(s)+r'(?!\\w)',t)]
  if hits: out[group]=hits
 return out
def flat(skills): return sorted({x for v in skills.values() for x in v})
def profile_from_text(text):
 email=(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+',text)or['Not found'])[0]; phone=(re.findall(r'(?:\+?\d[\d\s().-]{8,}\d)',text)or['Not found'])[0]
 lines=[x.strip() for x in text.splitlines() if x.strip()]; name=next((x for x in lines[:8] if len(x.split()) in (2,3) and '@' not in x and not re.search(r'\d',x)),'Candidate')
 skills=extract_skills(text); fs=flat(skills); sections={k:bool(re.search(k,text,re.I)) for k in ['education','experience','project','certification']}; score=min(96,35+len(fs)*4+sum(sections.values())*7+min(len(text)//250,15)); missing=[k.title() for k,v in sections.items() if not v]
 return {'name':name,'email':email,'phone':phone,'skills':skills,'all_skills':fs,'sections':sections,'resume_score':score,'missing_sections':missing,'strengths':(['Clear technical foundation'] if fs else [])+(['Project evidence present'] if sections['project'] else []),'suggestions':(['Add quantified project outcomes'] if sections['project'] else ['Add a projects section'])+(['Add '+', '.join(missing)+' details' if missing else 'Tailor your summary to the target role'])}
def match(profile):
 ps=profile.get('all_skills',[]); corpus=[' '.join(ps)+' '+profile.get('raw_text','')[:2500]]+[r['title']+' '+r['description']+' '+' '.join(r['required']+r['preferred']) for r in ROLES]; vec=TfidfVectorizer(ngram_range=(1,2),stop_words='english').fit_transform(corpus); sims=cosine_similarity(vec[0],vec[1:]).flatten(); out=[]
 for role,sim in zip(ROLES,sims):
  common=[s for s in role['required'] if s in ps]; missing=[s for s in role['required'] if s not in ps]; coverage=len(common)/len(role['required']); out.append({**role,'score':round(min(98,max(18,100*(.62*coverage+.38*sim)))),'matched_skills':common,'missing_skills':missing,'gap_percent':round(100*(1-coverage))})
 return sorted(out,key=lambda x:x['score'],reverse=True)
def roadmap(role_id,known):
 role=next((r for r in ROLES if r['id']==role_id),ROLES[0]); targets=[s for s in role['required']+role['preferred'] if s not in known]; items=[{'id':f'{role_id}-{i}','title':f'Master {s.title()}','description':f'Build practical confidence in {s} through focused practice and a portfolio artifact.','resource':RESOURCES.get(s,'Curated practice plan'),'completed':False,'weeks':2} for i,s in enumerate(targets[:6])]; return {'role':role['title'],'items':items or [{'id':'polish','title':'Polish your portfolio','description':'Turn your current strengths into outcome-focused projects.','resource':'Portfolio checklist','completed':False,'weeks':2}]}
KB=['Data scientists need Python, SQL, statistics, experimentation, and a portfolio of decisions supported by data.','Machine learning engineers combine models with Docker, APIs, evaluation, deployment, and monitoring.','For interviews, use STAR: situation, task, action, result; quantify outcomes and explain tradeoffs.','A strong AI project has a problem statement, data methodology, evaluation metric, demo, and clear README.']
def guidance(question,profile,matches):
 top=matches[0] if matches else None; ctx=sorted(KB,key=lambda x:len(set(question.lower().split())&set(x.lower().split())),reverse=True)[:2]
 return f"Based on your profile, **{top['title']}** is your strongest current direction ({top['score']}% match). You already bring {', '.join(top['matched_skills'][:4]) or 'a starting foundation'}. Prioritize **{', '.join(top['missing_skills'][:3]) or 'portfolio depth'}** next.\n\n{' '.join(ctx)}\n\nA practical next move: build one focused project, document its metric and tradeoffs, then rehearse a 90-second explanation." if top else 'Upload a resume first so I can ground guidance in your actual profile.'
def evaluate(answer):
 w=len(answer.split()); r=min(10,round(4+w/28,1)); d=min(10,round(3+len(re.findall(r'\b(example|because|metric|tradeoff|result|model|data)\b',answer.lower()))*1.2,1)); c=min(10,round(4+min(w,120)/24,1)); total=round((r+d+c)/3,1); return {'relevance':r,'technical_depth':d,'communication':c,'completeness':total,'overall':total,'feedback':'Strong structure.' if total>=7 else 'Add a specific example, measurable result, and explain your reasoning.','suggestion':'Use a concise STAR structure and name the technical tradeoff you made.'}
