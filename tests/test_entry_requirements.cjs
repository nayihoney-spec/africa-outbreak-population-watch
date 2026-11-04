const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tagName=tag;this.children=[];this.textContent='';this.attributes={};this.value='';}
 append(...children){this.children.push(...children)}
 replaceChildren(...children){this.children=children}
 setAttribute(k,v){this.attributes[k]=v}
 addEventListener(){}
}
const elements={};
const context={Intl,URL,Date,localStorage:{getItem:()=>null},document:{documentElement:{lang:'en'},createElement:tag=>new Element(tag),getElementById:id=>elements[id]||(elements[id]=new Element('div'))},window:{addEventListener(){}},T:{en:{}},AOPWData:{load:()=>new Promise(()=>{})}};
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/entry-requirements.js','utf8'),context);
vm.runInContext(fs.readFileSync('assets/advisories.js','utf8'),context);
const entry=context.AOPWEntryRequirements;
const now=Date.parse('2026-11-04T13:00:00Z');
assert.equal(entry.record.effective_at,'2026-11-03T23:59:00-05:00');
assert.equal(new Date(entry.record.effective_at).toISOString(),'2026-11-04T04:59:00.000Z');
assert.equal(entry.record.source_updated_at,'2026-11-03');
assert.equal(entry.record.checked_at,'2026-11-04');
assert.equal(entry.record.review_by,'2026-12-18');
assert.equal(entry.needsReview(now),false);
assert.equal(entry.needsReview(Date.parse('2026-11-06T00:00:00Z')),true);
assert.equal(entry.needsReview(Date.parse('2026-12-18T00:00:00Z')),true);
assert.equal(entry.needsReview(Date.parse('2026-11-03T00:00:00Z')),true);
const texts=node=>[node.textContent,...node.children.flatMap(texts)].filter(Boolean);
const expected=['en','zh-Hant','zh-Hans','ja','ko','th','fr','es','pt'];
assert.deepEqual(Object.keys(entry.copy),expected);
for(const language of expected){
 const t=entry.copy[language];assert.deepEqual(Object.keys(t),Object.keys(entry.copy.en));
 assert.ok(Object.values(t).every(v=>typeof v==='string'&&v.length>3));
 const row=entry.row(language,now),section=row.children[0].children[0];
 assert.equal(row.tagName,'tr');assert.equal(row.children[0].colSpan,6);
 assert.equal(section.lang,language);assert.equal(section.attributes['aria-labelledby'],'us-entry-title');
 const content=texts(section).join(' ');for(const key of ['title','scope','wait','exceptions','limits','validity'])assert.ok(content.includes(t[key]));
 assert.ok(content.includes('2026-11-03 23:59 EST (UTC−05:00)'));
 assert.ok(!content.includes(t.review));
 assert.ok(texts(entry.row(language,Date.parse('2026-12-19T00:00:00Z'))).includes(t.review));
 const links=section.children.at(-1).children;assert.deepEqual(links.map(x=>x.href),[entry.record.source,entry.record.order]);
 assert.ok(links.every(x=>x.target==='_blank'&&x.rel==='noopener noreferrer'));
}
// Rendered companion remains attached to US through sorting, repeated draws,
// language changes, and replacement of the canonical data object on reload.
vm.runInContext("DATA={items:[{code:'US',country:'United States',validation:'pending',url:'https://travel.state.gov/'},{code:'AU',country:'Australia',validation:'pending',url:'https://www.smartraveller.gov.au/'}]}",context);
for(const id of ['countrySearch','quickCountry'])elements[id]={value:''};
elements.advisoryStatus={value:'all'};elements.advisorySort={value:'name'};
for(const sort of ['name','name-desc','risk-high','source-date']){
 elements.advisorySort.value=sort;context.drawList();context.drawList();
 const rows=elements.countryList.children,extra=rows.findIndex(x=>x.className==='entry-requirement-row');
 assert.equal(rows.length,3);assert.ok(extra>0);assert.ok(rows[extra-1].children[0].textContent.endsWith('US'));
 assert.equal(elements.advisoryCount.textContent,'results_count: 2 / 2');
}
elements.quickCountry.value='AU';context.drawList();assert.equal(elements.countryList.children.length,1);
elements.quickCountry.value='US';context.drawList();assert.equal(elements.countryList.children.length,2);
context.document.documentElement.lang='zh-Hant';context.drawList();assert.ok(texts(elements.countryList).includes(entry.copy['zh-Hant'].title));
vm.runInContext("DATA={items:[{code:'US',country:'United States',validation:'verified',verified_at:new Date().toISOString(),url:'https://travel.state.gov/',level:'Level 4',source_updated_at:'2026-11-04'}]}",context);
context.drawList();assert.equal(elements.countryList.children.length,2);assert.equal(entry.record.checked_at,'2026-11-04');
const html=fs.readFileSync('pages/advisories.html','utf8');assert.ok(html.indexOf('entry-requirements.js')<html.indexOf('assets/advisories.js'));
console.log('PASS: nine languages, dates, official links, stale/expiry warning, US adjacency, filters, repeated rendering and refreshed-data independence.');
