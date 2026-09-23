import fs from 'node:fs';
import puppeteer from 'puppeteer-core';

const executablePath=process.env.CHROME_BIN;
if(!executablePath) throw new Error('CHROME_BIN is not set');

const browser=await puppeteer.launch({headless:true,executablePath,args:['--no-sandbox','--disable-dev-shm-usage']});
const profiles=[
  {name:'desktop',width:1440,height:900,deviceScaleFactor:1},
  {name:'mobile',width:390,height:844,deviceScaleFactor:2},
];
const results={generated_at:new Date().toISOString(),profiles:{}};
for(const p of profiles){
  const page=await browser.newPage();
  await page.setViewport({width:p.width,height:p.height,deviceScaleFactor:p.deviceScaleFactor});
  await page.goto('http://127.0.0.1:8000/prototypes/map26-100-benchmark.html?autorun=1',{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>window.__map26Benchmark?.done===true,{timeout:30000});
  results.profiles[p.name]=await page.evaluate(()=>window.__map26Benchmark);
  await page.close();
}
await browser.close();
fs.mkdirSync('artifacts',{recursive:true});
fs.writeFileSync('artifacts/map26-browser-benchmark.json',JSON.stringify(results,null,2)+'\n');
console.log('MAP26_BROWSER_BENCHMARK='+JSON.stringify(results));
