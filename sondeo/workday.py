import json, time, urllib.request
H={"User-Agent":"Mozilla/5.0 (compatible; buscador-empleo/1.0)","Accept":"application/json","Content-Type":"application/json"}
T=[l.split() for l in open("wd.txt").read().strip().splitlines()]
for host,tenant,site in T:
    url=f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    for q in ("Colombia",):
        try:
            req=urllib.request.Request(url,data=json.dumps({"appliedFacets":{},"limit":20,"offset":0,"searchText":q}).encode(),headers=H)
            with urllib.request.urlopen(req,timeout=25) as r:
                d=json.loads(r.read())
                jp=d.get("jobPostings",[])
                print("WD",host,site,d.get("total"),[(j.get("title"),j.get("locationsText"),j.get("postedOn")) for j in jp[:4]])
        except Exception as e: print("WD",host,site,"ERR",str(e)[:80])
        time.sleep(1.5)
