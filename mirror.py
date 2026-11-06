"""Retrieve public Swingora pages and localize their design assets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse,unquote
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,re,json,hashlib,shutil
ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'; REF=ROOT/'reference'; ASSETS=DIST/'assets'
ASSETS.mkdir(parents=True,exist_ok=True);REF.mkdir(exist_ok=True)
ORIGIN='https://swingora.webflow.io'
class Scan(HTMLParser):
 def __init__(self): super().__init__(); self.links=set();self.assets=set()
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  h=d.get('href','')
  if tag=='a':
   u=urlparse(urljoin(ORIGIN,h))
   if u.netloc=='swingora.webflow.io' and u.path and not re.search(r'\.[a-z0-9]{2,5}$',u.path): self.links.add(u.path)
  for a in ('src','poster','data-src'):
   if d.get(a,'').startswith(('https://','//')): self.assets.add(urljoin(ORIGIN,d[a]))
  if tag=='link' and h.startswith('https://') and d.get('rel')!='preconnect': self.assets.add(h)
  for item in d.get('srcset','').split(','):
   if item.strip(): self.assets.add(urljoin(ORIGIN,item.strip().split()[0]))
def fetch(url,path):
 for n in range(3):
  p=subprocess.run(['curl','-sSL','--fail','--max-time','65',url,'-o',str(path)],capture_output=True)
  if p.returncode==0:return True
 return False
pages={'/':Path('/tmp/swingora-reference.html').read_text()};visited={'/'};pending={'/'}
while pending:
 paths=set()
 for route in pending:
  p=Scan();p.feed(pages[route]);paths.update(p.links)
 paths-=visited;visited.update(paths);pending=set()
 if not paths:break
 with ThreadPoolExecutor(max_workers=7) as pool:
  jobs={pool.submit(fetch,ORIGIN+route,REF/(hashlib.sha256(route.encode()).hexdigest()[:12]+'.html')):route for route in paths}
  for job in as_completed(jobs):
   route=jobs[job];f=REF/(hashlib.sha256(route.encode()).hexdigest()[:12]+'.html')
   if job.result():pages[route]=f.read_text();pending.add(route);print('PAGE',route,flush=True)
   else: print('PAGE FAILED',route,flush=True)
assets=set()
for route,s in pages.items():
 p=Scan();p.feed(s);assets.update(p.assets)
 (REF/(('home' if route=='/' else route.strip('/').replace('/','__'))+'.html')).write_text(s)
# Remove third-party review/telemetry scripts, and retain only necessary design dependencies.
assets={u for u in assets if urlparse(u).netloc in ('cdn.prod.website-files.com','d3e54v103j8qbb.cloudfront.net','assets.website-files.com')}
local={};fail=[]
def localname(u):
 name=re.sub(r'[^a-zA-Z0-9._-]','_',unquote(urlparse(u).path.split('/')[-1]))
 return hashlib.sha256(u.encode()).hexdigest()[:10]+'-'+name
pending=assets
while pending:
 more=set()
 with ThreadPoolExecutor(max_workers=10) as pool:
  jobs={pool.submit(fetch,u,ASSETS/localname(u)):u for u in pending}
  for job in as_completed(jobs):
   u=jobs[job]
   if not job.result():fail.append(u);continue
   name=localname(u);local[u]='/assets/'+name
   if name.endswith(('.css','.js')):
    txt=(ASSETS/name).read_text()
    if name.endswith('.css'):
     for a in re.findall(r'url\([\"\']?([^\)\"\']+)',txt):
      if not a.startswith('data:'):more.add(urljoin(u,a))
    # Webflow split-runtime files may load extra chunks.
    for a in re.findall(r'[\"\'](https://cdn\.prod\.website-files\.com/[^\"\'\s<>]+)[\"\']',txt):more.add(a)
 pending=more-local.keys()-set(fail)
 print('ASSETS',len(local),'remaining',len(pending),flush=True)
# Resolve all asset references in pages and CSS while preserving original responsive markup.
for u,path in local.items():
 if path.endswith(('.css','.js')):
  file=DIST/path.lstrip('/');s=file.read_text()
  if path.endswith('.css'):
   s=re.sub(r'url\(([\"\']?)([^\)\"\']+)\1\)',lambda m:'url('+m[1]+local.get(urljoin(u,m[2]),m[2])+m[1]+')',s)
  for src,dst in sorted(local.items(),key=lambda x:-len(x[0])):s=s.replace(src,dst)
  file.write_text(s)
for route,s in pages.items():
 # Drop the published review bridge, review script, and external validator.
 s=re.sub(r'<script\b[^>]*>\s*window\.__WF_REVIEW_BRIDGE.*?</script>','',s,flags=re.S)
 s=re.sub(r'<script\b[^>]*src=[\"\'][^\"\']*validation-worker[^>]*>.*?</script>','',s,flags=re.S)
 s=s.replace('data-wf-domain="swingora.webflow.io"','data-wf-domain="swingora-recreation.muhirwa250.chatgpt.site"')
 for src,dst in sorted(local.items(),key=lambda x:-len(x[0])):s=s.replace(src,dst)
 s=s.replace(ORIGIN+'/', '/')
 # Remove integrity hashes because localized CSS paths are rewritten.
 s=re.sub(r'\s+integrity="[^"]*"','',s)
 s=s.replace('</head>','<link rel="stylesheet" href="/replica.css"/></head>')
 s=s.replace('</body>','<script src="/replica.js"></script></body>')
 out=DIST/route.lstrip('/')/'index.html' if route!='/' else DIST/'index.html'
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(s)
(ROOT/'inventory.json').write_text(json.dumps({'routes':sorted(pages),'assets':local,'failed':fail},indent=2))
print('DONE',len(pages),'pages',len(local),'assets','failures',len(fail),flush=True)
