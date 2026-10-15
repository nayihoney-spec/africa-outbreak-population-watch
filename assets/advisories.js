const fallback=[["US","United States"],["GB","United Kingdom"],["AU","Australia"],["CA","Canada"],["CN","China (Mainland)"],["HK","Hong Kong SAR"],["MO","Macao SAR"],["TW","Taiwan"],["JP","Japan"],["KR","South Korea"],["TH","Thailand"],["MY","Malaysia"],["SG","Singapore"],["FR","France"],["DE","Germany"],["IT","Italy"],["ES","Spain"],["PT","Portugal"],["NL","Netherlands"],["BE","Belgium"],["CH","Switzerland"],["AT","Austria"],["SE","Sweden"],["NO","Norway"],["DK","Denmark"],["FI","Finland"],["IE","Ireland"],["NZ","New Zealand"],["IN","India"],["ID","Indonesia"],["PH","Philippines"],["VN","Vietnam"],["AE","United Arab Emirates"],["SA","Saudi Arabia"],["ZA","South Africa"],["KE","Kenya"],["UG","Uganda"],["RW","Rwanda"],["BI","Burundi"],["TZ","Tanzania"],["ZM","Zambia"],["AO","Angola"],["CG","Republic of the Congo"],["SS","South Sudan"],["CF","Central African Republic"]];
let DATA,selected=null;
const $=id=>document.getElementById(id);
const lang=()=>localStorage.getItem('aopw-lang')||document.documentElement.lang||'en';
const tr=k=>(T[lang()]||T.en)?.[k]||T.en?.[k]||k;
function countryName(x){try{return new Intl.DisplayNames([lang()],{type:'region'}).of(x.code)||x.country}catch(e){return x.country}}
function fresh(x,now=Date.now()){const at=Date.parse(x.verified_at);return x.validation==='verified'&&Number.isFinite(at)&&now>=at&&now-at<48*3600000}
function hasSource(x){try{return new URL(x.url).protocol==='https:'}catch(e){return false}}
function risk(x){if(!fresh(x))return null;const normalized=(x.normalized||'').toLowerCase();if(/region|area-dependent/.test(normalized))return null;return ({'very high':4,'high':3,'moderate':2,'medium':2,'low':1})[normalized]??null}
function comparison(x){if(!fresh(x))return tr('not_verified');const rank=risk(x);return rank?tr(({4:'very_high',3:'high',2:'moderate',1:'low'})[rank]):tr('regional')}
function validationText(x){return fresh(x)?tr('verified'):tr('not_verified')}
function officialDates(x){const issued=x.source_published_at,updated=x.source_updated_at;if(issued&&updated&&issued!==updated)return tr('date_published')+': '+issued+' · '+tr('date_updated')+': '+updated;return updated||issued||tr('date_unavailable')}
function officialDateTime(x){return Date.parse(x.source_updated_at||x.source_published_at)||0}
function orderedRows(items,{query='',country='',status='all',sort='name'}={}){
 const q=query.trim().toLocaleLowerCase(lang());
 const exactCode=items.some(x=>x.code.toLowerCase()===q);
 const nameOrder=(a,b)=>countryName(a).localeCompare(countryName(b),lang())||a.code.localeCompare(b.code);
 return items.filter(x=>(!country||x.code===country)&&(!q||(exactCode?x.code.toLowerCase()===q:[countryName(x),x.country,x.code].some(v=>(v||'').toLocaleLowerCase(lang()).includes(q))))&&(status!=='verified'||fresh(x))&&(status!=='sources'||hasSource(x))).sort((a,b)=>{
  if(sort==='name-desc')return -nameOrder(a,b);
  if(sort==='risk-high'||sort==='risk-low'){
   // Unverified data and regional advice are not fabricated numeric levels.
   const group=x=>!fresh(x)?2:risk(x)==null?1:0;
   const groups=group(a)-group(b);if(groups)return groups;
   const ar=risk(a),br=risk(b);if(ar!=null&&br!=null&&ar!==br)return sort==='risk-high'?br-ar:ar-br;
  }
  if(sort==='source-date'){const delta=officialDateTime(b)-officialDateTime(a);if(delta)return delta;}
  if(sort==='checked'){
   const af=fresh(a),bf=fresh(b);if(af!==bf)return af?-1:1;
   const delta=(Date.parse(b.verified_at)||0)-(Date.parse(a.verified_at)||0);if(delta)return delta;
  }
  return nameOrder(a,b);
 });
}
function selectCountry(code,{focus=false}={}){const hit=DATA.items.find(x=>x.code===code);if(!hit)return;selected=hit;localStorage.setItem('aopw-country',code);drawList();render();if(focus){$('result').focus({preventScroll:true});$('result').scrollIntoView({behavior:'smooth',block:'start'})}}
function populateCountries(){const current=$('quickCountry').value;const all=document.createElement('option');all.value='';all.textContent=tr('all_countries');$('quickCountry').replaceChildren(all);for(const x of orderedRows(DATA.items)){const option=document.createElement('option');option.value=x.code;option.textContent=countryName(x)+' · '+x.code;$('quickCountry').append(option)}$('quickCountry').value=current||''}
function cell(row,text){const td=document.createElement('td');td.textContent=text;row.append(td);return td}
function drawList(){if(!DATA)return;const rows=orderedRows(DATA.items,{query:$('countrySearch').value,country:$('quickCountry').value,status:$('advisoryStatus').value,sort:$('advisorySort').value});$('countryList').replaceChildren();for(const x of rows){const row=document.createElement('tr');row.className=selected?.code===x.code?'advisory-selected':'';const td=document.createElement('td'),button=document.createElement('button');button.type='button';button.className='advisory-country';button.textContent=countryName(x)+' · '+x.code;button.setAttribute('aria-label',tr('select_detail')+': '+countryName(x));button.setAttribute('aria-pressed',String(selected?.code===x.code));button.addEventListener('click',()=>selectCountry(x.code,{focus:true}));td.append(button);row.append(td);const levelCell=cell(row,fresh(x)?x.level:tr('not_verified'));levelCell.className='advisory-level';levelCell.lang=x.source_language||lang();if(x.alert_type==='epidemic-risk'){const kind=document.createElement('small');kind.textContent=tr('epidemic_risk')+(x.risk_assessed_at?' · '+tr('risk_assessed_at')+': '+x.risk_assessed_at:'');levelCell.append(kind)}const c=cell(row,comparison(x));c.className='advisory-risk risk-'+(risk(x)||'unknown');cell(row,officialDates(x));const check=cell(row,fresh(x)?x.verified_at.replace('T',' ').replace(/\..*$/,' UTC'):tr('not_verified'));if(x.last_attempt_status==='blocked'){const warning=document.createElement('small');warning.textContent=tr('read_blocked');check.append(warning)}const sourceCell=document.createElement('td');if(hasSource(x)){const a=document.createElement('a');a.href=x.url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=x.source_name||tr('open_official');sourceCell.append(a);if(x.registry_url&&x.registry_url!==x.url){const portal=document.createElement('a');portal.href=x.registry_url;portal.target='_blank';portal.rel='noopener noreferrer';portal.textContent=tr('source_portal');const small=document.createElement('small');small.append(portal);sourceCell.append(small)}}else sourceCell.textContent=tr('no_source');row.append(sourceCell);$('countryList').append(row)}$('advisoryCount').textContent=tr('results_count')+': '+rows.length+' / '+DATA.items.length;$('advisoryEmpty').hidden=rows.length>0}
function render(){if(!selected)return;$('rCountry').textContent=countryName(selected);$('rLevel').textContent=fresh(selected)?selected.level:tr('not_verified');$('rNorm').textContent=comparison(selected);$('rLevel').lang=selected.source_language||lang();$('rSourceDate').textContent=officialDates(selected);$('rChecked').textContent=fresh(selected)?selected.verified_at:tr('not_verified');$('rSource').textContent=selected.source_name||tr('no_source');$('official').href=hasSource(selected)?selected.url:'#';$('official').hidden=!hasSource(selected);$('mode').textContent=tr('data_mode')+': '+validationText(selected)+' · '+tr('registry_updated')+' '+DATA.updated_at+(selected.travel_advice?' · '+tr('original_advice')+': '+selected.travel_advice:'')+(selected.alert_type==='epidemic-risk'?' · '+tr('epidemic_risk')+(selected.risk_assessed_at?' · '+tr('risk_assessed_at')+': '+selected.risk_assessed_at:''):'')+(selected.last_attempt_status==='blocked'?' · '+tr('read_blocked'):'')}
async function load(){DATA=structuredClone((await AOPWData.load()).advisories);const known=new Set(DATA.items.map(x=>x.code));fallback.forEach(([code,country])=>{if(!known.has(code))DATA.items.push({code,country,validation:'pending',url:'#'})});populateCountries();selected=DATA.items.find(x=>x.code===localStorage.getItem('aopw-country'))||DATA.items.find(x=>x.code==='US')||DATA.items[0];drawList();render()}
$('result').setAttribute('tabindex','-1');
$('backBtn').addEventListener('click',()=>history.back());
$('countrySearch').addEventListener('input',drawList);
for(const id of ['quickCountry','advisorySort','advisoryStatus'])$(id).addEventListener('change',()=>{drawList();if(id==='quickCountry'&&$(id).value)selectCountry($(id).value)});
$('resetFilters').addEventListener('click',()=>{$('countrySearch').value='';$('quickCountry').value='';$('advisoryStatus').value='all';$('advisorySort').value='name';drawList()});
$('detect').addEventListener('click',async()=>{const button=$('detect'),span=button.querySelector('span');button.disabled=true;span.textContent=tr('detecting');try{const r=await fetch('https://ipwho.is/',{signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('IP suggestion unavailable');const x=await r.json();if(DATA.items.some(i=>i.code===x.country_code)){$('countrySearch').value='';$('quickCountry').value=x.country_code;$('advisoryStatus').value='all';selectCountry(x.country_code)}}catch(e){}finally{button.disabled=false;span.textContent=tr('detect')}});
window.addEventListener('aopw-language',()=>{if(DATA){populateCountries();drawList();render()}});
load().catch(()=>{$('advisoryEmpty').hidden=false;$('advisoryEmpty').textContent=tr('load_error')});
