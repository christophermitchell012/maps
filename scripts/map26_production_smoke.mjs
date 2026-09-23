import fs from 'node:fs';
import puppeteer from 'puppeteer-core';

const executablePath=process.env.CHROME_BIN;
if(!executablePath) throw new Error('CHROME_BIN is not set');
const browser=await puppeteer.launch({headless:true,executablePath,args:['--no-sandbox','--disable-dev-shm-usage']});
const out={generated_at:new Date().toISOString(),profiles:{}};
for(const p of [{name:'desktop',width:1440,height:900,scale:1},{name:'mobile',width:390,height:844,scale:2}]){
  const page=await browser.newPage();
  await page.setViewport({width:p.width,height:p.height,deviceScaleFactor:p.scale});
  await page.setRequestInterception(true);
  page.on('request',req=>{
    const u=req.url();
    if(u.includes('tile.openstreetmap.org')||u.includes('gibs.earthdata.nasa.gov')) req.abort();
    else req.continue();
  });
  const t0=Date.now();
  await page.goto('http://127.0.0.1:8000/26-dark-sky-tonight.html',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.__map26RankingsReady===true,{timeout:30000});
  const data=await page.evaluate(()=>({
    ready:window.__map26RankingsReady,
    perf:window.__map26RankingPerf,
    bestRows:document.querySelectorAll('#ranklist .rankrow').length,
    status:document.getElementById('rankstatus')?.textContent,
  }));
  data.wallMs=Date.now()-t0;
  if(!data.ready || data.bestRows!==10) throw new Error(`${p.name}: ranking UI failed ${JSON.stringify(data)}`);
  out.profiles[p.name]=data;
  await page.close();
}
await browser.close();
fs.mkdirSync('artifacts',{recursive:true});
fs.writeFileSync('artifacts/map26-production-browser-smoke.json',JSON.stringify(out,null,2)+'\n');
console.log('MAP26_PRODUCTION_BROWSER='+JSON.stringify(out));
