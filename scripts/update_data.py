"""Fail-closed, dependency-free official-source refresh. published.json is atomic authority."""
import argparse, copy, datetime as dt, hashlib, html, json, os, pathlib, re, sys, tempfile, urllib.request
from urllib.parse import urlsplit
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
CDC='https://www.cdc.gov/ebola/situation-summary/index.html'
ECDC='https://www.ecdc.europa.eu/en/ebola-outbreak-democratic-republic-congo-and-uganda'
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style','noscript'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style','noscript'):self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def plain(raw):
 p=Text();p.feed(raw);return re.sub(r'\s+',' ',html.unescape(' '.join(p.parts))).strip()
def number(x):return int(re.sub(r'[,\s]','',x))
def date(x):
 x=x.strip().replace('.','')
 for f in ('%b %d, %Y','%B %d, %Y','%d %B %Y'):
  try:return dt.datetime.strptime(x,f).date().isoformat()
  except ValueError:pass
 raise ValueError('Unrecognized source date: '+x)
def parse_cdc(raw):
 text=plain(raw);section=re.search(r'Total Cases\s*\(as of\s+([^)]*)\)(.{0,2500})',text,re.I)
 if not section:raise ValueError('CDC total-cases section missing')
 m=re.search(r'Democratic Republic of the Congo\s+([\d,\s]+) confirmed cases\s+([\d,\s]+) confirmed deaths',section[2],re.I)
 if not m:raise ValueError('CDC DRC-specific confirmed counts missing')
 return {'name':'CDC','url':CDC,'report_as_of':date(section[1]),'cases':number(m[1]),'deaths':number(m[2]),'evidence':m[0][:240],'sha256':hashlib.sha256(raw.encode()).hexdigest()}
def parse_ecdc(raw):
 text=plain(raw)
 m=re.search(r'As of (\d{1,2} \w+ \d{4}), the Democratic Republic of the Congo \(DRC\) (?:has )?reported a total of ([\d,\s]+) confirmed cases, including ([\d,\s]+) related deaths(?: \(from data up until (\d{1,2} \w+)\))?',text,re.I)
 if not m:raise ValueError('ECDC DRC-specific confirmed counts missing')
 asof=date(m[1]);through=date(m[4]+' '+asof[:4]) if m[4] else asof
 return {'name':'ECDC','url':ECDC,'report_as_of':asof,'data_through':through,'cases':number(m[2]),'deaths':number(m[3]),'evidence':m[0][:350],'sha256':hashlib.sha256(raw.encode()).hexdigest()}
class OfficialRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if urlsplit(newurl).scheme!='https' or urlsplit(newurl).hostname not in ('www.cdc.gov','www.ecdc.europa.eu'):raise ValueError('Redirect outside official allowlist')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Africa-Outbreak-Population-Watch/2.0 (+https://github.com/nayihoney-spec/africa-outbreak-population-watch)'})
 with urllib.request.build_opener(OfficialRedirect()).open(req,timeout=25) as r:
  raw=r.read(2_000_001)
  if len(raw)>2_000_000:raise ValueError('Source size limit exceeded')
  return raw.decode('utf-8')
def atomic(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile('w',dir=path.parent,delete=False,encoding='utf-8') as f:
  json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');tmp=f.name
 os.replace(tmp,path)
def validate(bundle):
 assert bundle['schema_version']==1
 events=bundle['outbreaks']['events'];assert len({e['id'] for e in events})==len(events)
 for e in events:assert type(e['cases']) is int and type(e['deaths']) is int and 0<=e['deaths']<=e['cases']
 rows=[x for x in bundle['latest']['outbreaks'] if x.get('confirmed_cases') is not None];assert rows
 current=rows[-1];event=next(e for e in events if e['id']=='2026-bundibugyo')
 assert (current['confirmed_cases'],current['confirmed_deaths'],current['as_of'])==(event['cases'],event['deaths'],event['as_of'])
 assert bundle['verification']['status']=='verified'
 evidence=bundle['verification']['sources'];assert len(evidence)>=2
 assert all((e['cases'],e['deaths'])==(current['cases'],current['deaths']) for e in evidence)
 assert len({x['code'] for x in bundle['advisories']['items']})==len(bundle['advisories']['items'])
 for a in bundle['advisories']['items']:assert a['url'].startswith('https://')
 return True
def promote(bundle,sources,now):
 a,b=sources
 for x in sources:
  assert 0<=x['deaths']<=x['cases'] and type(x['cases']) is int
  age=(dt.date.fromisoformat(now[:10])-dt.date.fromisoformat(x['report_as_of'])).days
  if not 0<=age<=14:raise ValueError('Source date is future or older than 14 days')
 if (a['cases'],a['deaths'])!=(b['cases'],b['deaths']):raise ValueError('CDC/ECDC counts differ; retain published bundle for review')
 asof=a['report_as_of']  # Primary CDC reporting date; secondary dates remain attached to evidence.
 out=copy.deepcopy(bundle);row=next(x for x in out['latest']['outbreaks'] if x['year']==2026)
 if asof<row['as_of']:raise ValueError('Source data date regressed')
 if a['cases']<row['cases'] or a['deaths']<row['deaths']:raise ValueError('Cumulative values decreased; correction requires documented review')
 for key in ['cases','deaths']:
  if row[key] and a[key]>row[key]*1.5:raise ValueError('Cumulative jump exceeds 50%; review required')
 row.update(cases=a['cases'],deaths=a['deaths'],confirmed_cases=a['cases'],confirmed_deaths=a['deaths'],as_of=asof,verification_status='Verified official-source comparison; shared upstream may exist',primary_source='CDC / ECDC',primary_source_as_of=asof,cfr_percent=round(a['deaths']/a['cases']*100,2))
 row.pop('recovered',None)
 event=next(x for x in out['outbreaks']['events'] if x['id']=='2026-bundibugyo');event.update(cases=a['cases'],deaths=a['deaths'],as_of=asof,source='CDC / ECDC',source_url=CDC,case_basis='laboratory-confirmed cases and deaths; DRC only')
 out['outbreaks']['updated_at']=now;out['latest']['generated_at']=now
 out['verification']={'status':'verified','checked_at':now,'scope':'DRC only; 2026 outbreak; confirmed cases and deaths','method':'Two official publishers agree on counts; reporting dates retained separately. Shared upstream data is not independent epidemiological confirmation.','sources':sources}
 out['published_at']=now;out['revision']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()[:16]
 validate(out);return out
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--fixtures',type=pathlib.Path);args=parser.parse_args()
 now=dt.datetime.now(dt.timezone.utc).isoformat();status={'checked_at':now,'status':'failed','published_changed':False}
 try:
  bundle=json.loads((ROOT/'data/published.json').read_text())
  sources=[parse_cdc((args.fixtures/'cdc.html').read_text() if args.fixtures else fetch(CDC)),parse_ecdc((args.fixtures/'ecdc.html').read_text() if args.fixtures else fetch(ECDC))]
  candidate=promote(bundle,sources,now)
  # All validation completed before publication; readers fetch this single atomic object.
  atomic(ROOT/'data/published.json',candidate)
  for key,name in [('latest','latest'),('outbreaks','outbreaks'),('advisories','advisories')]:atomic(ROOT/f'data/{name}.json',candidate[key])
  status.update(status='passed',published_changed=True,revision=candidate['revision'],counts={'cases':sources[0]['cases'],'deaths':sources[0]['deaths']},sources=[x['url'] for x in sources])
 except Exception as e:status['error']=str(e)[:400]
 atomic(ROOT/'data/maintenance.json',status)
 print(json.dumps(status))
 return 0 if status['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
