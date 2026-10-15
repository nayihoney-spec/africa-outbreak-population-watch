AOPWData.load().catch(()=>{const p=document.createElement("p");p.textContent="Data unavailable / 資料暫時無法讀取";document.querySelector("main").prepend(p)});
