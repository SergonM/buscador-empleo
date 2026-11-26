import re, urllib.request, json
H={"User-Agent":"Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Mobile Safari/537.36","Accept-Language":"es-CO,es;q=0.9","Accept":"text/html,application/json"}
def get(u, data=None, h=None):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,data=data,headers={**H,**(h or {})}),timeout=30)
        return r.status, r.read().decode("utf-8","replace")
    except Exception as e: return str(e)[:80], ""
for u in ["https://co.computrabajo.com/trabajo-de-analista-de-datos-en-bogota-dc",
          "https://co.computrabajo.com/trabajo-de-practicante-ingenieria-de-sistemas",
          "https://www.elempleo.com/co/ofertas-empleo/bogota/analista-de-datos",
          "https://www.magneto365.com/co/empleos/analista-de-datos",
          "https://www.magneto365.com/co/trabajos/ofertas-empleo-en-bogota?q=analista%20de%20datos"]:
    c,b=get(u); print("=====",u,c,len(b))
    if not b: continue
    print("TITLE",re.findall(r"<title>(.*?)</title>",b,re.S)[:1])
    print("ARTICLES",len(re.findall(r"<article",b)), "LDJSON",len(re.findall(r"application/ld\+json",b)), "NEXTDATA", "__NEXT_DATA__" in b)
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>',b,re.S)[:2]: print("LD",m[:500])
    i=b.find("<article"); print("ART0",re.sub(r"\s+"," ",b[i:i+2500]) if i>=0 else "")
    i=b.find("__NEXT_DATA__"); print("ND",b[i:i+1500] if i>=0 else "")
    for k in ("api/","/api","offers","jobOffers","ofertas"): 
        print("K",k,list(set(re.findall(r'["\'](https?://[^"\']*'+re.escape(k)+r'[^"\']*)',b)))[:5])
