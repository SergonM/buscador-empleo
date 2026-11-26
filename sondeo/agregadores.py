import json, urllib.request
UA={"User-Agent":"Mozilla/5.0 (compatible; buscador-empleo/1.0)","Accept":"application/json"}
def t(nombre,url,data=None,h=None):
    try:
        req=urllib.request.Request(url,data=data,headers={**UA,**(h or {})})
        with urllib.request.urlopen(req,timeout=30) as r:
            b=r.read().decode("utf-8","replace")
            print("AGR",nombre,r.status,len(b),b[:600].replace("\n"," "))
    except Exception as e: print("AGR",nombre,"ERR",str(e)[:120])
t("jobicy","https://jobicy.com/api/v2/remote-jobs?count=50&geo=latam")
t("jobicy-tag","https://jobicy.com/api/v2/remote-jobs?count=20&tag=data")
t("remoteok","https://remoteok.com/api")
t("wwr","https://weworkremotely.com/categories/remote-programming-jobs.rss")
t("arbeitnow","https://www.arbeitnow.com/api/job-board-api")
t("torre","https://search.torre.co/opportunities/_search/?size=5&lang=es&aggregate=false",data=json.dumps({"and":[{"location":{"term":"Colombia"}},{"skill/role":{"text":"data analyst","experience":"potential-to-develop"}}]}).encode(),h={"Content-Type":"application/json"})
t("torre2","https://search.torre.co/opportunities/_search/?size=5&lang=es",data=json.dumps({"skill/role":{"text":"data analyst","experience":"potential-to-develop"}}).encode(),h={"Content-Type":"application/json"})
t("careerjet","http://public.api.careerjet.net/search?locale_code=es_CO&keywords=analista%20datos&location=Bogota&affid=213e213hd12344552&user_ip=1.1.1.1&user_agent=Mozilla&pagesize=5")
t("computrabajo-rss","https://co.computrabajo.com/rss/trabajo-de-analista-de-datos")
t("elempleo","https://www.elempleo.com/co/ofertas-empleo/?trabajo=analista%20de%20datos")
t("workingnomads","https://www.workingnomads.com/api/exposed_jobs/")
t("himalayas-browse","https://himalayas.app/jobs/api?limit=20&offset=0")
t("magneto","https://www.magneto365.com/co/empleos")
t("lever-meli","https://api.lever.co/v0/postings/mercadolibre?mode=json")
t("meli-eightfold","https://mercadolibre.eightfold.ai/api/apply/v2/jobs?domain=mercadolibre.com&location=Colombia&num=5")
t("smartr-search","https://api.smartrecruiters.com/v1/companies/Globant/postings?country=co&limit=5")
t("workday-meli","https://mercadolibre.wd3.myworkdayjobs.com/wday/cxs/mercadolibre/MeliCareers/jobs",data=b'{"limit":5,"offset":0,"searchText":"analyst"}',h={"Content-Type":"application/json"})
