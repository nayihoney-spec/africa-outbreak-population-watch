const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const element=()=>({value:'cases',textContent:'',options:[],addEventListener(){},replaceChildren(){},append(){},setAttribute(){}}),els=new Map(),get=id=>{if(!els.has(id))els.set(id,element());return els.get(id)};
const context={Intl,Date,URL,console,localStorage:{getItem:()=>null,setItem(){}},navigator:{language:'en'},CustomEvent:function(){},document:{documentElement:{lang:'en'},querySelectorAll:()=>[],querySelector:()=>null,getElementById:id=>id==='lang'?null:get(id),createElement:()=>element()},window:{addEventListener(){},dispatchEvent(){}},AOPWData:{load:()=>new Promise(()=>{})}};
vm.createContext(context);for(const f of ['assets/i18n.js','assets/outbreak-labels.js','assets/outbreak.js'])vm.runInContext(fs.readFileSync(f,'utf8'),context);
vm.runInContext(`
for(const language of OUTBREAK_LANGS){
 for(const key of OUTBREAK_KEYS)if(!T[language][key])throw Error(language+': '+key);
 for(const key of Object.keys(OUTBREAK_PLACES))if(!OUTBREAK_PLACES[key][OUTBREAK_LANGS.indexOf(language)])throw Error('Missing place translation');
 document.documentElement.lang=language;
 if(!Number.isFinite(calculateRows([{cases:10,deaths:1},{cases:30,deaths:3}],'share')[1].value))throw Error('Invalid value');
}
`,context);
const data=[{cases:10,deaths:1},{cases:30,deaths:3}];assert.equal(context.calculateRows(data,'share')[0].value,.25);assert.equal(context.calculateRows(data,'share')[1].value,1);assert.equal(context.calculateRows(data,'cumcases')[1].value,40);assert.equal(context.calculateRows(data,'cfr')[1].value,.1);
const bundle=JSON.parse(fs.readFileSync('data/published.json','utf8'));context.bundle=bundle;vm.runInContext('outbreakBundle=bundle;document.documentElement.lang="zh-Hant";summary()',context);assert.equal(get('cumCases').textContent,new Intl.NumberFormat('zh-Hant').format(bundle.latest.outbreaks.at(-1).confirmed_cases));assert.equal(get('cumDeaths').textContent,new Intl.NumberFormat('zh-Hant').format(bundle.latest.outbreaks.at(-1).confirmed_deaths));console.log('PASS: nine languages, geographic labels, cumulative-share math, and current confirmed cards independent of historical sums.');
