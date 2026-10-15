"""Extract destination-specific alert fields. Never promote a link availability check."""
import concurrent.futures, copy, datetime as dt, hashlib, json, pathlib, re, sys, urllib.request
from urllib.parse import urlsplit
from html.parser import HTMLParser
from update_data import plain, atomic, validate, date
ROOT=pathlib.Path(__file__).resolve().parents[1]
URLS={'CN':'https://cs.mfa.gov.cn/zyxx/202607/t20260723_11990742.html','TW':'https://www.boca.gov.tw/sp-trwa-content-3100-f3f00-1.html','US':'https://travel.state.gov/en/international-travel/travel-advisories/destination.cod.html','AU':'https://www.smartraveller.gov.au/destinations/africa/democratic-republic-congo','GB':'https://www.gov.uk/foreign-travel-advice/democratic-republic-of-the-congo','CA':'https://travel.gc.ca/destinations/congo-kinshasa','SG':'https://www.mfa.gov.sg/travelling-overseas/travel-advisories-notices-and-visa-information/democratic-republic-of-congo/','JP':'https://www.anzen.mofa.go.jp/info/pcinfectionspothazardinfo_103.html'}
ALLOWED={urlsplit(x).hostname for x in URLS.values()}
class Redirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if urlsplit(newurl).scheme!='https' or urlsplit(newurl).hostname not in ALLOWED:raise ValueError('Redirect outside official allowlist')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch_once(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; Africa-Outbreak-Population-Watch/2.1)','Accept':'text/html'})
 with urllib.request.build_opener(Redirect()).open(req,timeout=25) as r:
  b=r.read(2_000_001)
  if len(b)>2_000_000:raise ValueError('Page too large')
  return b.decode('utf-8-sig')
def fetch(url):
 error=None
 for attempt in range(2):
  try:return fetch_once(url)
  except (TimeoutError, OSError) as exc:error=exc
 raise error
class Rows(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  if t in ('td','th') and self.row is not None:self.cell=[]
 def handle_data(self,d):
  if self.cell is not None:self.cell.append(d)
 def handle_endtag(self,t):
  if t in ('td','th') and self.cell is not None:
   if self.row is not None:self.row.append(re.sub(r'\s+',' ',''.join(self.cell)).strip())
   self.cell=None
  if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
def require(pattern,text):
 m=re.search(pattern,text,re.I)
 if not m:raise ValueError('Required destination-specific field missing: '+pattern[:70])
 return m

def parse_boca(raw):
 p=Rows();p.feed(raw);fields={x[0]:x[1] for x in p.rows if len(x)>=2}
 if fields.get('國家地區')!='剛果民主共和國':raise ValueError('Wrong BOCA destination')
 updated=fields.get('發布/更新日期');level=fields.get('警示等級')
 if not updated or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',updated):raise ValueError('BOCA alert-row date missing')
 if not level or not re.fullmatch(r'第[一二三四]級[：:]\s*[\u4e00-\u9fff\s]+',level):raise ValueError('BOCA warning level missing')
 return {'level':level,'normalized':'Very high' if level.startswith('第四級') else 'High' if level.startswith('第三級') else 'Moderate' if level.startswith('第二級') else 'Low','source_published_at':None,'source_updated_at':updated,'source_date_kind':'published_or_updated','source_language':'zh-Hant','source_field_labels':['發布/更新日期','警示等級'],'evidence':level}
def parse_us(raw):
 text=plain(raw);section=require(r'Travel advisory\s*[-–—]\s*Democratic Republic of the Congo(.{0,700})',text)[1]
 level=require(r'(Level [1-4]\s*[-–—]\s*(?:Do not travel|Reconsider travel|Exercise increased caution|Exercise normal precautions))',section)[1]
 issued=date(require(r'Date issued:\s*(\w+ \d{1,2}, \d{4})',section)[1])
 updated=date(require(r'Last Updated:\s*(\w+ \d{1,2}, \d{4})',text)[1])
 return {'level':level,'normalized':{'4':'Very high','3':'High','2':'Moderate','1':'Low'}[require(r'Level ([1-4])',level)[1]],'source_published_at':issued,'source_updated_at':updated,'source_date_kind':'separate','source_language':'en','evidence':level}
def parse_au(raw):
 text=plain(raw);level=require(r'Overall:\s*(Do not travel|Reconsider your need to travel|Exercise a high degree of caution|Exercise normal safety precautions)',text)[1]
 updated=date(require(r'Updated:\s*(\d{1,2} \w+ \d{4})',text)[1])
 return {'level':level,'normalized':{'Do not travel':'Very high','Reconsider your need to travel':'High','Exercise a high degree of caution':'Moderate','Exercise normal safety precautions':'Low'}[level],'source_published_at':None,'source_updated_at':updated,'source_date_kind':'updated','source_language':'en','evidence':level}
def parse_gb(raw):
 text=plain(raw);require(r'FCDO.*?advises against all travel to parts of Democratic Republic of the Congo',text);require(r'advises against all but essential travel to parts of Democratic Republic of the Congo',text)
 updated=date(require(r'Still current at:\s*\d{1,2} \w+ \d{4}\s*Updated:\s*(\d{1,2} \w+ \d{4})',text)[1])
 return {'level':'Against all travel / all but essential travel to parts of DRC','normalized':'Region-dependent','source_published_at':None,'source_updated_at':updated,'source_date_kind':'updated','source_language':'en','evidence':'FCDO regional warnings apply.'}
def parse_ca(raw):
 text=plain(raw);require(r'DEMOCRATIC REPUBLIC OF THE CONGO\s*[-–—]\s*AVOID ALL TRAVEL',text)
 updated=date(require(r'Last updated:\s*(\d{1,2} \w+ \d{4})',text)[1])
 return {'level':'AVOID ALL TRAVEL','normalized':'Very high','source_published_at':None,'source_updated_at':updated,'source_date_kind':'updated','source_language':'en','evidence':'AVOID ALL TRAVEL'}
def parse_sg(raw):
 text=plain(raw);section=require(r'Travel Advisory:\s*Ministry of Health \(MOH\) Public Health Advisory\s*(\d{1,2} \w+ \d{4})(.{0,450})',text)
 require(r'Singaporeans are advised to defer all non-essential travel to the DRC',section[2])
 return {'level':'Defer all non-essential travel to the DRC','normalized':'High','source_published_at':date(section[1]),'source_updated_at':None,'source_date_kind':'published','source_language':'en','evidence':'Defer all non-essential travel to the DRC'}
def parse_jp(raw):
 text=plain(raw);require(r'コンゴ民主共和国',text)
 m=require(r'(\d{4})年\s*(\d{2})月\s*(\d{2})日(.{0,2500})',text)
 section=m[4]
 for level in '１２３４':require('レベル'+level,section)
 if not ('地域' in section and '退避' in section):raise ValueError('Japanese regional scope missing')
 return {'level':'レベル４：退避勧告／レベル３：渡航中止勧告／レベル２：不要不急の渡航中止／レベル１：十分注意（地域別）','normalized':'Region-dependent','source_published_at':None,'source_updated_at':'-'.join(m.group(i) for i in [1,2,3]),'source_date_kind':'updated','source_language':'ja','evidence':'地域別の危険情報'}
def parse_cn(raw):
 text=plain(raw)
 require(r'提醒中国公民近期谨慎前往刚果[（(]金[）)]',text)
 stamp=require(r'发布时间[：:]\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})',text)
 require(r'世界卫生组织将刚果[（(]金[）)]本国疫情风险等级上调至[“「\"]极高风险[”」\"]',text)
 require(r'非必要不前往',text)
 return {'level':'极高风险','normalized':'Very high','source_published_at':stamp[1],'source_published_raw':stamp[1]+' '+stamp[2],'source_updated_at':None,'source_date_kind':'published','source_language':'zh-Hans','alert_type':'epidemic-risk','assessment_authority':'WHO, quoted by China Consular Services','risk_geography':'DRC','risk_assessed_at':'2026-05-22' if '5月17日' in text and '22日' in text and stamp[1].startswith('2026-05') else None,'travel_advice':'谨慎前往，非必要不前往','evidence':'疫情风险等级：极高风险','registry_url':'https://cs.mfa.gov.cn/','url':URLS['CN'],'source_name':'中国领事服务网'}
PARSERS={'CN':parse_cn,'TW':parse_boca,'US':parse_us,'AU':parse_au,'GB':parse_gb,'CA':parse_ca,'SG':parse_sg,'JP':parse_jp}
def extract(code):
 raw=fetch(URLS[code]);record=PARSERS[code](raw)
 for key in ['source_published_at','source_updated_at']:
  if record[key] and dt.date.fromisoformat(record[key])>dt.datetime.now(dt.timezone.utc).date()+dt.timedelta(days=1):raise ValueError('Future official date')
 record['source_content_sha256']=hashlib.sha256(raw.encode()).hexdigest();return record

def main():
 bundle=json.loads((ROOT/'data/published.json').read_text());now=dt.datetime.now(dt.timezone.utc).isoformat();audit={'checked_at':now,'passed':[],'blocked':{},'unconfigured':[]}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  results={code:pool.submit(extract,code) for code in PARSERS}
  for row in bundle['advisories']['items']:
   code=row['code']
   if code not in results:audit['unconfigured'].append(code);continue
   try:
    record=results[code].result();row.update(record,validation='verified',verified_at=now,checked=now,last_attempt_status='passed');row.pop('last_attempt_error',None);audit['passed'].append(code)
   except Exception as e:
    row.update(last_attempt_status='blocked',last_attempt_error=str(e)[:250]);audit['blocked'][code]=str(e)[:250]
   row['last_attempt_at']=now
 bundle['advisories']['updated_at']=now;bundle['published_at']=now;bundle['revision']=hashlib.sha256(json.dumps(bundle,sort_keys=True).encode()).hexdigest()[:16]
 validate(bundle);atomic(ROOT/'data/published.json',bundle);atomic(ROOT/'data/advisories.json',bundle['advisories']);atomic(ROOT/'data/advisory-maintenance.json',audit)
 status_path=ROOT/'data/maintenance.json'
 if status_path.exists():
  status=json.loads(status_path.read_text());status['revision']=bundle['revision'];status['advisory_status']='blocked' if audit['blocked'] else 'passed';status['advisory_checked_at']=now;atomic(status_path,status)
 print(json.dumps(audit,ensure_ascii=False));return 1 if audit['blocked'] else 0
if __name__=='__main__':sys.exit(main())
