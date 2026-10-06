"""Build a single-file, backend-free demo page: python -m scripts.build_demo [out.html]
Answers come from the real pipeline, captured at build time, so the page is shareable as-is."""
import base64, json, os, sys
os.environ.update(DATABASE_PATH=":memory:", ADMIN_TOKEN="x", OPENAI_API_KEY="", RATE_LIMIT_PER_MIN="1000")
from fastapi.testclient import TestClient
from app.main import create_app

QS = ["Who is Ajanta Luhana?", "Where has Ajanta worked?", "Tell me about the quadcopter UAV project", "What is VisionEye?",
      "Which certifications does Ajanta have?", "How does RAG work?", "What technologies does Ajanta use?",
      "How can I contact Ajanta?", "Tell me about Metavystic HRMIS", "What projects has Ajanta built?",
      "Does Ajanta have Oracle certifications?", "How does RAG reduce hallucination?"]
c = TestClient(create_app())
demo = {q: c.post("/api/chat", json={"message": q}).text for q in QS}
demo["__fallback__"] = c.post("/api/chat", json={"message": "What is Ajanta's salary?"}).text
hire = c.post("/api/hire", json={"role_type": "Freelance", "scope": "LLM agents and video analytics", "skills": ["RAG", "LLM agents", "YOLO", "Django"]}).json()
photo = "data:image/jpeg;base64," + base64.b64encode(open("frontend/ajanta.jpg", "rb").read()).decode()
h = open("frontend/index.html", encoding="utf-8").read()
h = h.replace('<img src="ajanta.jpg" alt="Ajanta Luhana" onerror="this.remove()">', '<img id="stagePhoto" alt="Ajanta Luhana" onerror="this.remove()">')
h = h.replace('<img src="ajanta.jpg" alt="" onerror="this.parentNode', '<img src="\'+PHOTO+\'" alt="" onerror="this.parentNode')
shim = """const PHOTO=%s;const DEMO=%s;const HIRE=%s;
document.getElementById('stagePhoto').src=PHOTO;
const _nw=s=>s.toLowerCase().replace(/[^a-z0-9 ]/g,' ').split(/\\s+/).filter(w=>w.length>2),_sl=ms=>new Promise(r=>setTimeout(r,ms)),_f=window.fetch.bind(window);
window.fetch=async(u,o)=>{u=String(u);
 if(u.includes('/api/chat')){const w=new Set(_nw(JSON.parse(o.body).message));let best=null,bs=0;
  for(const k in DEMO){if(k=='__fallback__')continue;const kw=_nw(k),s=kw.filter(x=>w.has(x)).length/Math.max(kw.length,1);if(s>bs){bs=s;best=k}}
  await _sl(1300);const body=DEMO[bs>=.5?best:'__fallback__'];
  return new Response(new ReadableStream({start(c){c.enqueue(new TextEncoder().encode(body));c.close()}}),{status:200,headers:{'Content-Type':'text/event-stream'}})}
 if(u.includes('/api/feedback'))return new Response('{"ok":true}');
 if(u.includes('/api/hire')){await _sl(700);return new Response(JSON.stringify(HIRE))}
 return _f(u,o)};
document.querySelector('.brand').insertAdjacentHTML('afterend','<small style="color:#a695c9;margin-left:.6rem">demo preview</small>');
""" % (json.dumps(photo), json.dumps(demo), json.dumps(hire))
h = h.replace("<script>\nconst $=", "<script>\n" + shim + "const $=", 1)
out = sys.argv[1] if len(sys.argv) > 1 else "ajanta-ai-demo.html"
open(out, "w", encoding="utf-8").write(h)
print(out, len(h) // 1024, "KB")
