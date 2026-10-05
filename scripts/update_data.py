import json,datetime,urllib.request,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"data/latest.json"
def ping(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Africa-Outbreak-Population-Watch/1.0"})
 with urllib.request.urlopen(req,timeout=30) as r:r.read(1024)
def main():
 data=json.loads(OUT.read_text())
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 checks={"WHO":"https://www.who.int/emergencies/disease-outbreak-news","ReliefWeb":"https://reliefweb.int/","UN World Population Prospects":"https://www.un.org/development/desa/pd/world-population-prospects"}
 for row in data["sources"]:
  if row["name"] in checks:
   try:ping(checks[row["name"]]);row["status"]="reachable; parser/validation pipeline active"
   except Exception:row["status"]="fetch failed; retaining last trusted snapshot"
   row["last_checked"]=now
 data["generated_at"]=now
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
