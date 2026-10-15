const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const bundle=JSON.parse(fs.readFileSync('data/published.json','utf8')),code=fs.readFileSync('assets/data-client.js','utf8');
async function scenario(mode){
 const calls=[],el={setAttribute(){},replaceChildren(){},append(){},prepend(){}};
 const context={URL,Date,AbortSignal,location:{pathname:'/'},window:{addEventListener(){}},document:{currentScript:{src:'https://example.test/assets/data-client.js'},documentElement:{lang:'en'},getElementById:()=>el,createElement:()=>({...el}),createTextNode:x=>x,querySelector:()=>el},fetch:async url=>{calls.push(url);if(url.includes('maintenance.json'))return {ok:true,json:async()=>({status:'passed'})};if(url.includes('raw.githubusercontent.com')&&mode==='offline')throw Error('offline');let data=structuredClone(bundle);if(url.includes('raw.githubusercontent.com')&&mode==='invalid')data.outbreaks.events.at(-1).cases++;return {ok:true,json:async()=>data}}};
 vm.createContext(context);vm.runInContext(code,context);const result=await context.AOPWData.load();assert.equal(result.revision,bundle.revision);assert.equal(result.latest.outbreaks.at(-1).cases,result.outbreaks.events.at(-1).cases);assert.equal(calls.some(x=>x.startsWith('https://example.test/data/published.json')),mode!=='online');
 assert.throws(()=>context.AOPWData.validate({...bundle,schema_version:99}));
}
(async()=>{for(const mode of ['online','offline','invalid'])await scenario(mode);console.log('PASS: canonical live bundle, offline fallback, invalid live bundle fallback, view consistency.');})().catch(e=>{console.error(e);process.exitCode=1});
