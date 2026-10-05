const fmt=n=>n==null?"—":Number(n).toLocaleString();
async function loadHome(){
  const status=document.getElementById("status");
  try{
    const d=await(await fetch("data/latest.json?t="+Date.now(),{cache:"no-store"})).json();
    const latest=d.outbreaks.filter(x=>x.cases!=null).at(-1);
    document.getElementById("cases").textContent=fmt(latest.confirmed_cases??latest.cases);
    document.getElementById("deaths").textContent=fmt(latest.confirmed_deaths??latest.deaths);
    document.getElementById("date").textContent="As of "+latest.as_of;
    const a=await(await fetch("data/advisories.json?t="+Date.now(),{cache:"no-store"})).json();
    document.getElementById("count").textContent=a.items.length;
    if(status)status.textContent="Latest validated snapshot · "+(d.generated_at||"source timestamped");
  }catch(e){
    if(status)status.textContent="Snapshot temporarily unavailable";
  }
}
loadHome();