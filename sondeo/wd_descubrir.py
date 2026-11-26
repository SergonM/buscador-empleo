import json, sys, time, urllib.request, urllib.error, re
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36"}
class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op=urllib.request.build_opener(NoRedir)
def jobs(host,t,site):
    try:
        req=urllib.request.Request(f"https://{host}/wday/cxs/{t}/{site}/jobs",data=json.dumps({"appliedFacets":{},"limit":1,"offset":0,"searchText":"Colombia"}).encode(),headers={**H,"Accept":"application/json","Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=20) as r: return json.loads(r.read()).get("total")
    except urllib.error.HTTPError as e: return f"E{e.code}"
    except Exception as e: return "ERR"
for t in sys.argv[1].split(","):
    hall=None
    for n in (1,5,3,12,10,103,108,102,501):
        host=f"{t}.wd{n}.myworkdayjobs.com"
        try:
            r=op.open(urllib.request.Request(f"https://{host}/",headers=H),timeout=12); loc=r.geturl(); code=r.status
        except urllib.error.HTTPError as e:
            code=e.code; loc=e.headers.get("Location","")
        except Exception as e:
            continue
        if code in (301,302,303,307,308) and loc and "community.workday" not in loc and "invalid" not in loc.lower():
            m=re.search(r"myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([^/?#]+)",loc)
            if m:
                site=m.group(1); time.sleep(1.2); tot=jobs(host,t,site)
                print("WDX",host,t,site,tot,flush=True); hall=1; break
        time.sleep(0.3)
    if not hall: print("WDX-NO",t,flush=True)
