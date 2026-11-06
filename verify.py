from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import json,re
root=Path(__file__).parent/'dist'
errors=[];links=0
class Check(HTMLParser):
 def handle_starttag(self,tag,attrs):
  global links
  d=dict(attrs)
  for key in ('src','href','poster'):
   url=d.get(key,'')
   if not url.startswith('/') or url.startswith('//'):continue
   path=unquote(urlparse(url).path)
   dest=root/path.lstrip('/')
   links+=1
   if not (dest.is_file() or (dest/'index.html').is_file()):errors.append(str(page)+': '+url)
  if 'data-turnstile-sitekey' in d:errors.append('External form challenge: '+str(page))
for page in root.rglob('*.html'):
 s=page.read_text();Check().feed(s)
 if 'validation-worker' in s or '__WF_REVIEW_BRIDGE' in s:errors.append('Review telemetry: '+str(page))
 if '/replica.js' not in s:errors.append('Missing local form guard: '+str(page))
assets=json.loads((root.parent/'inventory.json').read_text())
for asset in root.glob('assets/*.css'):
 for url in re.findall(r'url\([\"\']?(/assets/[^\)\"\']+)',asset.read_text()):
  if not (root/url.lstrip('/')).is_file():errors.append('Missing font or background: '+url)
if errors:
 print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(assets["routes"])} pages, {len(assets["assets"])} assets, {links} local references; forms are local-only; no review telemetry.')
