import re,pathlib,sys,tomllib
R=pathlib.Path(__file__).resolve().parent.parent
cfg=tomllib.loads((R/'netlify.toml').read_text())
rules=cfg.get('redirects',[])
def exists(path):
    p=path.split('?')[0]
    if p.endswith('/'): return (R/p.strip('/')/'index.html').exists() if p!='/' else (R/'index.html').exists()
    if (R/p.lstrip('/')).is_file(): return True
    if (R/p.lstrip('/')/'index.html').exists(): return 'slash'
    return False
def match(rule_from,path):
    pat='^'+re.escape(rule_from).replace(r'\*','.*')+'$'
    return re.match(pat,path)
def resolve(url,depth=0):
    path=url.split('?')[0]
    e=exists(path)
    if e is True: return (200,path)
    if e=='slash': return resolve(path+'/',depth+1)
    for r in rules:
        if match(r['from'],path):
            if r.get('status',301)==404: return (404,path)
            return resolve(r['to'],depth+1) if depth<5 else (508,path)
    return (404,path)
urls=[l.strip() for l in open(sys.argv[1]) if l.strip()]
bad=[]
for u in urls:
    code,final=resolve(u)
    if code!=200: bad.append((u,code))
print(f'{len(urls)} old URLs tested; {len(urls)-len(bad)} resolve to a live page; failures: {bad}')
