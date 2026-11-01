const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const bundle=JSON.parse(fs.readFileSync('data/published.json','utf8')),code=fs.readFileSync('assets/data-client.js','utf8');
async function scenario(mode){
 const rendered=[],calls=[],el={setAttribute(){},replaceChildren(){},append(x){if(x?.textContent)rendered.push(x.textContent)},prepend(){}};
 const context={URL,Date,AbortSignal,location:{pathname:'/'},window:{addEventListener(){}},document:{currentScript:{src:'https://example.test/assets/data-client.js'},documentElement:{lang:'en'},getElementById:()=>el,createElement:()=>({...el}),createTextNode:x=>x,querySelector:()=>el},fetch:async url=>{calls.push(url);if(url.includes('maintenance.json'))return {ok:true,json:async()=>({status:'passed'})};if(url.includes('raw.githubusercontent.com')&&mode==='offline')throw Error('offline');let data=structuredClone(bundle);if(url.includes('raw.githubusercontent.com')&&mode==='invalid')data.outbreaks.events.at(-1).cases++;return {ok:true,json:async()=>data}}};
 vm.createContext(context);vm.runInContext(code,context);const result=await context.AOPWData.load();assert.equal(result.revision,bundle.revision);assert.equal(result.latest.outbreaks.at(-1).cases,result.outbreaks.events.at(-1).cases);assert.equal(calls.some(x=>x.startsWith('https://example.test/data/published.json')),mode!=='online');
 assert.ok(rendered.some(x=>x.startsWith('Outbreak data:')));assert.ok(rendered.some(x=>x.startsWith('Travel advisory checks:')));
 assert.throws(()=>context.AOPWData.validate({...bundle,schema_version:99}));
}
(async()=>{for(const mode of ['online','offline','invalid'])await scenario(mode);console.log('PASS: canonical live bundle, offline fallback, invalid live bundle fallback, view consistency.');})().catch(e=>{console.error(e);process.exitCode=1});
// Historical verification and current attempted checks are separate states.
{
 const context={URL,document:{currentScript:{src:'https://example.test/assets/data-client.js'}}};vm.createContext(context);vm.runInContext(code,context);
 const d={advisories:{items:[{code:'US',validation:'verified',verified_at:'2026-11-01T00:00:00Z',last_attempt_at:'2026-11-01T05:00:00Z',last_attempt_status:'blocked'},{code:'AU',validation:'verified',verified_at:'2026-11-01T06:00:00Z',last_attempt_at:'2026-11-01T05:00:00Z',last_attempt_status:'blocked'},{code:'FR',validation:'pending'}]}};
 const state=context.AOPWData.advisoryHealth(d);assert.deepEqual(Array.from(state.blocked),['US']);assert.deepEqual(Array.from(state.unconfigured),['FR']);assert.equal(d.advisories.items[0].validation,'verified');
 d.advisories.items[0].last_attempt_status='passed';assert.equal(context.AOPWData.advisoryHealth(d).blocked.length,0);
}
