import json, sys, time, urllib.request, urllib.parse
UA={"User-Agent":"Mozilla/5.0 (compatible; buscador-empleo/1.0)","Accept":"application/json"}
def get(url, data=None, h=None):
    try:
        req=urllib.request.Request(url, data=data, headers={**UA, **(h or {})})
        with urllib.request.urlopen(req, timeout=25) as r:
            b=r.read().decode("utf-8","replace")
            try: return r.status, json.loads(b)
            except Exception: return r.status, b
    except urllib.error.HTTPError as e: return e.code, None
    except Exception as e: return str(e)[:60], None
KEYS=("colombia","bogot","latam","latin america","south america","americas","remote","remoto")
def cnt(locs):
    t=[l.lower() for l in locs]
    return len(t), sum(any(k in x for k in ("colombia","bogot")) for x in t), sum(any(k in x for k in KEYS) for x in t)
slugs=sys.argv[1].split(",")
for s in slugs:
    out=[]
    c,d=get(f"https://boards-api.greenhouse.io/v1/boards/{s}/jobs")
    if c==200 and isinstance(d,dict): out.append(("gh",cnt([j.get("location",{}).get("name","") for j in d.get("jobs",[])])))
    c,d=get(f"https://api.lever.co/v0/postings/{s}?mode=json")
    if c==200 and isinstance(d,list): out.append(("lever",cnt([(j.get("categories") or {}).get("location","")+" "+" ".join((j.get("categories") or {}).get("allLocations") or [])+" "+(j.get("workplaceType") or "") for j in d])))
    c,d=get(f"https://api.ashbyhq.com/posting-api/job-board/{s}")
    if c==200 and isinstance(d,dict): out.append(("ashby",cnt([(j.get("location") or "")+" "+" ".join(a.get("location","") for a in j.get("secondaryLocations") or [])+(" remote" if j.get("isRemote") else "") for j in d.get("jobs",[])])))
    c,d=get(f"https://api.smartrecruiters.com/v1/companies/{s}/postings?limit=100&country=co")
    if c==200 and isinstance(d,dict) and d.get("totalFound"): out.append(("sr",cnt([json.dumps(j.get("location",{})) for j in d.get("content",[])]),d.get("totalFound")))
    c,d=get(f"https://apply.workable.com/api/v1/widget/accounts/{s}")
    if c==200 and isinstance(d,dict) and d.get("jobs"): out.append(("workable",cnt([json.dumps(j.get("locations") or [j.get("country","")]) for j in d["jobs"]])))
    c,d=get(f"https://{s}.recruitee.com/api/offers/")
    if c==200 and isinstance(d,dict) and d.get("offers"): out.append(("recruitee",cnt([(j.get("location") or "")+" "+(j.get("country") or "") for j in d["offers"]])))
    print("SLUG", s, out, flush=True)
    time.sleep(0.3)
