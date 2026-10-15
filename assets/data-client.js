/* One atomic, versioned data bundle for all views. No source-page HTML is executed. */
(function(global){
'use strict';
const REMOTE='https://raw.githubusercontent.com/nayihoney-spec/africa-outbreak-population-watch/main/data/published.json';
const here=new URL('../',document.currentScript.src), LOCAL=new URL('data/published.json',here).href;
let promise,healthFailure=null,refreshNotice=()=>{};
function validate(d){
 if(d?.schema_version!==1||d.verification?.status!=='verified'||!Array.isArray(d.outbreaks?.events)||!Array.isArray(d.advisories?.items))throw Error('Invalid bundle');
 const current=d.latest.outbreaks.filter(x=>x.confirmed_cases!=null).at(-1),event=d.outbreaks.events.find(x=>x.id==='2026-bundibugyo');
 if(!current||!event||current.cases!==event.cases||current.deaths!==event.deaths||current.as_of!==event.as_of)throw Error('Inconsistent views');
 for(const e of d.outbreaks.events)if(!Number.isInteger(e.cases)||!Number.isInteger(e.deaths)||e.deaths<0||e.deaths>e.cases)throw Error('Invalid counts');
 if(!d.verification.sources?.length||d.verification.sources.some(e=>!['https://www.cdc.gov/ebola/situation-summary/index.html','https://www.ecdc.europa.eu/en/ebola-outbreak-democratic-republic-congo-and-uganda'].includes(e.url))||d.verification.sources.some(e=>e.cases!==current.cases||e.deaths!==current.deaths))throw Error('Evidence mismatch');
 const walk=v=>{if(typeof v==='string'&&/[<>\u0000]/.test(v))throw Error('Unexpected markup');if(v&&typeof v==='object')Object.values(v).forEach(walk)};walk(d);
 if(d.advisories.items.some(x=>!/^https:\/\//.test(x.url)||!/^\w{2}$/.test(x.code)))throw Error('Invalid advisory');
 if(!Number.isFinite(Date.parse(d.published_at))||Date.parse(d.published_at)>Date.now()+300000)throw Error('Invalid publication time');
 return d;
}
async function read(url){const r=await fetch(url+'?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('Data HTTP '+r.status);return validate(await r.json())}
function lang(){return document.documentElement.lang||'en'}
const labels={en:['Data verified','Bundled fallback','Data through','Source checked','Data snapshot is over 48 hours old; check official sources','History uses reported event totals; current outbreak uses confirmed counts.'], 'zh-Hant':['資料已核對','備援快照','數據截至','來源檢查時間','資料快照已超過 48 小時，請查看官方來源','歷史事件採報告總數；目前疫情採確診數，統計口徑不同。'],'zh-Hans':['数据已核对','备用快照','数据截至','来源检查时间','数据快照已超过48小时，请查看官方来源','历史事件采用报告总数；当前疫情采用确诊数，统计口径不同。'],ja:['データ照合済み','保存済みデータ','データ基準日','確認日時','48時間以上経過：公式情報をご確認ください','過去は報告総数、現在の流行は確定例です。'],ko:['자료 대조 완료','저장된 자료','자료 기준일','확인 시간','48시간 경과: 공식 출처를 확인하세요','과거는 보고 총계, 현재 유행은 확진 건수입니다.'],th:['ตรวจสอบข้อมูลแล้ว','ข้อมูลสำรอง','ข้อมูลถึงวันที่','ตรวจสอบเมื่อ','ข้อมูลเกิน 48 ชั่วโมง โปรดตรวจสอบแหล่งทางการ','ข้อมูลในอดีตเป็นยอดรายงาน ส่วนการระบาดปัจจุบันเป็นผู้ป่วยยืนยัน'],fr:['Données comparées','Copie de secours','Données au','Vérifié le','Plus de 48 heures : consulter les sources officielles','Historique : totaux signalés ; épidémie actuelle : cas confirmés.'],es:['Datos cotejados','Copia de respaldo','Datos hasta','Verificado','Más de 48 horas: consulte fuentes oficiales','Histórico: totales notificados; brote actual: casos confirmados.'],pt:['Dados comparados','Cópia de segurança','Dados até','Verificado','Mais de 48 horas: consulte fontes oficiais','Histórico: totais notificados; surto atual: casos confirmados.']};
function notice(d,fallback){
 let el=document.getElementById('dataHealth');if(!el){el=document.createElement('aside');el.id='dataHealth';el.className='notice';el.setAttribute('role','status');document.querySelector('main')?.prepend(el)}
 const render=()=>{const t=labels[lang()]||labels.en;const current=d.latest.outbreaks.filter(x=>x.confirmed_cases!=null).at(-1);const stale=Date.now()-Date.parse(d.verification.checked_at)>48*3600000;el.replaceChildren();const msg=document.createElement('p');msg.textContent=[fallback?t[1]:t[0],t[2]+': '+current.as_of,t[3]+': '+d.verification.checked_at,({en:'Version','zh-Hant':'資料版本','zh-Hans':'数据版本',ja:'データ版',th:'รุ่นข้อมูล',ko:'자료 버전',fr:'Version',es:'Versión',pt:'Versão'}[lang()]||'Version')+': '+d.revision].join(' · ');el.append(msg);if(stale){const p=document.createElement('p');p.textContent=t[4];el.append(p)}for(const s of d.verification.sources){const a=document.createElement('a');a.href=s.url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=s.name+' ('+s.report_as_of+')';el.append(a,document.createTextNode(' · '))}if(healthFailure){const warning=document.createElement('p');warning.textContent='⚠ '+t[1]+' · '+healthFailure;el.append(warning)}if(location.pathname.includes('outbreak')){const note=document.createElement('p');note.textContent=t[5];el.append(note)}};
 refreshNotice=render;render();window.addEventListener('aopw-language',render);
}
async function load(){let d,fallback=false;try{d=await read(REMOTE)}catch(e){fallback=true;d=await read(LOCAL)}notice(d,fallback);try{const r=await fetch(REMOTE.replace('published.json','maintenance.json')+'?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(5000)});if(r.ok){const h=await r.json();if(h.status!=='passed'&&Date.parse(h.checked_at)>=Date.parse(d.verification.checked_at)){healthFailure=h.checked_at;refreshNotice()}}}catch(e){}return d}
global.AOPWData={load:()=>promise||(promise=load()),validate};
})(globalThis);
