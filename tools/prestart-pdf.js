/* Renders a day's Prestart PDF exactly as the board's "Prestart PDF" button
   does, without a browser on site. Used by the daily scheduled task that
   files each signed-off prestart into the Prestarts folder.

   node tools/prestart-pdf.js <dump.json> <YYYY-MM-DD> <out.pdf>

   dump.json is {table: rows} in the shape the board's REST reads return:
   lifts as columns, every other table as {id, data}. The board runs from
   this checkout on a local port with those rows served in place of the
   database, then buildPDF("all") writes the file. */
const {chromium}=require('playwright');
const fs=require('fs'), http=require('http'), path=require('path');
const [dumpPath, day, outPath]=process.argv.slice(2);
if(!dumpPath||!/^\d{4}-\d{2}-\d{2}$/.test(day||'')||!outPath){
  console.error('usage: node tools/prestart-pdf.js <dump.json> <YYYY-MM-DD> <out.pdf>'); process.exit(2);
}
const DUMP=JSON.parse(fs.readFileSync(dumpPath,'utf8'));
const ROOT=path.resolve(__dirname,'..');
const TYPES={'.html':'text/html','.js':'application/javascript','.css':'text/css','.png':'image/png','.svg':'image/svg+xml','.woff2':'font/woff2','.json':'application/json'};
const srv=http.createServer((req,res)=>{
  let p=decodeURIComponent(req.url.split('?')[0]); if(p.endsWith('/')) p+='index.html';
  const f=path.join(ROOT,p);
  if(!f.startsWith(ROOT)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){res.writeHead(404);return res.end();}
  let body=fs.readFileSync(f);
  if(p==='/board/index.html') body=body.toString().replace('function sectionText(which){',
    'window.__eliseTools={setDate:function(d){setDate(d)},pdf:function(w){return buildPDF(w)}};function sectionText(which){');
  res.writeHead(200,{'Content-Type':TYPES[path.extname(p)]||'application/octet-stream'}); res.end(body);
});
function filterRows(rows, url){
  const q=new URL(url).searchParams; let out=rows.slice();
  for(const [k,v] of q){
    if(['select','order','limit','offset'].includes(k)) continue;
    const m=/^(eq|neq|gte|lte|gt|lt|in)\.(.*)$/.exec(v); if(!m) continue;
    const op=m[1], val=m[2];
    out=out.filter(r=>{
      const x=(k in r)?r[k]:(r.data&&k in r.data?r.data[k]:undefined);
      if(x===undefined) return true;
      const s=String(x);
      if(op==='eq') return s===val; if(op==='neq') return s!==val;
      if(op==='gte') return s>=val; if(op==='lte') return s<=val;
      if(op==='gt') return s>val; if(op==='lt') return s<val;
      if(op==='in') return val.replace(/^\(|\)$/g,'').split(',').map(t=>t.replace(/^"|"$/g,'')).includes(s);
      return true;
    });
  }
  return out;
}
(async()=>{
  await new Promise(r=>srv.listen(0,'127.0.0.1',r));
  const port=srv.address().port;
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1280,height:900},timezoneId:'Australia/Brisbane'});
  const p=await ctx.newPage(); const errs=[];
  p.on('pageerror',e=>errs.push(e.message));
  /* registered first so it is matched last: anything not stubbed below is refused */
  await p.route(/^https?:\/\/(?!127\.0\.0\.1)/,r=>r.abort());
  await p.route('**/rest/v1/**',r=>{
    const u=r.request().url(); if(r.request().method()!=='GET') return r.fulfill({status:403,body:'{}'});
    const t=/\/rest\/v1\/([a-z_]+)/.exec(u)[1];
    r.fulfill({status:200,contentType:'application/json',body:JSON.stringify(filterRows(DUMP[t]||[],u))});
  });
  await p.route('**/auth/v1/**',r=>r.fulfill({status:200,contentType:'application/json',body:'{}'}));
  await p.goto(`http://127.0.0.1:${port}/board/#prestart`);
  await p.waitForFunction(()=>window.__eliseTools&&window.jspdf,null,{timeout:20000});
  await p.waitForTimeout(1500);
  await p.evaluate(d=>window.__eliseTools.setDate(d),day);
  await p.waitForTimeout(2500);
  const data=await p.evaluate(async()=>{const d=await window.__eliseTools.pdf('all');return d?d.output('datauristring'):null;});
  await b.close(); srv.close();
  if(!data){ console.error('PDF did not build', errs); process.exit(1); }
  fs.writeFileSync(outPath, Buffer.from(data.split(',')[1],'base64'));
  console.log('wrote', outPath, fs.statSync(outPath).size, 'bytes', errs.length?('page errors: '+errs.join(' | ')):'');
})().catch(e=>{console.error(e);process.exit(1);});
