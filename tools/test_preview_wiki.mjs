import { createServer } from 'node:http';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

const browserPath = process.env.WIKI_BROWSER;
if (!browserPath) throw new Error('Set WIKI_BROWSER to a Chrome or Edge executable');
const head = 'a'.repeat(40), base = 'b'.repeat(40);
const objects = new Map(), files = {};
function add(name, data) {
  const bytes = Buffer.from(data);
  const hash = createHash('sha256').update(bytes).digest('hex');
  files[name] = hash;
  objects.set(hash, JSON.stringify({data: bytes.toString('base64')}));
}
const wikiIndex = await readFile('wiki/index.html', 'utf8');
const probe = `<script>document.addEventListener('DOMContentLoaded', () => {
  const box = document.querySelector('#search');
  box.value = '星穹'; box.dispatchEvent(new Event('input', {bubbles:true}));
  const result = document.querySelector('#results a');
  parent.postMessage({type:'test:home', search:!!result, count:document.querySelector('#pagecount')?.textContent, styled:getComputedStyle(document.querySelector('.topbar')).display}, '*');
  setTimeout(() => document.querySelector('.quick-a').click(), 100);
});</script>`;
add('index.html', wikiIndex.replace('</body>', probe + '</body>'));
for (const name of ['assets/style.css','data/titles.js','data/stats.js','data/link_report.js','assets/app.js','assets/home.js','assets/theme.js','assets/character-panel.js']) add(name, await readFile('wiki/' + name));
let article = await readFile('wiki/pages/character/角色.html', 'utf8');
for (const match of article.matchAll(/src="\.\.\/\.\.\/(assets\/icons\/[^\"]+)"/g)) {
  const name = decodeURIComponent(match[1]);
  add(name, await readFile('wiki/' + name));
}
article = article.replace('</body>', `<script>document.addEventListener('DOMContentLoaded',()=>{ const image=document.querySelector('img[src^="data:"]'); parent.postMessage({type:'test:next',title:document.title,prose:!!document.querySelector('.prose'),image:!!image,css:!!document.querySelector('link[href^="data:text/css"]')}, '*'); });</script></body>`);
add('pages/character/角色.html', article);
const manifest = {version: 1, repo:'ganmayou2333/hsr-knowledge-base', pr:37, head, base, run:1, run_attempt:1, trusted_run:2, trusted_attempt:1, files};
let canaries = 0, stale = false;
const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    if (url.pathname === '/canary') { canaries++; res.writeHead(204).end(); return; }
    if (url.pathname === '/previews/37/manifest.json') { res.setHeader('Content-Type','application/json'); res.end(JSON.stringify(manifest)); return; }
    const match = /^\/previews\/37\/objects\/([0-9a-f]{64})\.json$/.exec(url.pathname);
    if (match && objects.has(match[1])) { res.setHeader('Content-Type','application/json'); res.end(objects.get(match[1])); return; }
    const names = {'/':'index.html', '/shell.js':'shell.js', '/frame.js':'frame.js', '/shell.css':'shell.css'};
    const name = names[url.pathname];
    if (!name) { res.writeHead(404).end(); return; }
    res.setHeader('Content-Type', name.endsWith('.js') ? 'text/javascript' : name.endsWith('.css') ? 'text/css' : 'text/html');
    let content = await readFile(path.join('preview_shell', name), 'utf8');
    if (name === 'index.html' && process.argv.includes('--without-frame-policy')) {
      content = content.replace(/\s*<meta http-equiv="Content-Security-Policy" content="frame-src 'none'">/, '');
    }
    res.end(content);
  } catch { res.writeHead(500).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const profile = await mkdtemp(path.join(tmpdir(), 'hsr-preview-browser-'));
const browser = spawn(browserPath, ['--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'], {stdio:'ignore'});
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
let socket;
try {
  let port;
  for (let i=0;i<300;i++) {
    try { port = Number((await readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0]); break; }
    catch { if (browser.exitCode !== null) throw new Error('Browser exited'); await wait(100); }
  }
  if (!port) throw new Error('Browser did not start');
  const info = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  socket = new WebSocket(info.webSocketDebuggerUrl);
  await new Promise((resolve,reject) => {socket.onopen=resolve; socket.onerror=reject;});
  let id=0; const pending=new Map();
  function send(method, params={}, sessionId) {
    const command = {id:++id,method,params,...(sessionId ? {sessionId} : {})};
    return new Promise((resolve,reject) => {pending.set(command.id,{resolve,reject}); socket.send(JSON.stringify(command)); setTimeout(() => {if(pending.delete(command.id)) reject(new Error('CDP timeout: '+method));},15000).unref();});
  }
  socket.onmessage = event => {
    const m=JSON.parse(event.data);
    if (m.id && pending.has(m.id)) { const p=pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result); }
    if (m.method === 'Fetch.requestPaused') {
      const url = m.params.request.url;
      const isRunList = url.includes('/actions/workflows/') && url.includes('/runs?');
      const trustedList = isRunList && url.includes('wiki-trusted-data.yml');
      const data = isRunList ? {workflow_runs:[{id:trustedList ? 2 : 1,run_attempt:1,event:trustedList ? 'pull_request_target' : 'pull_request',path:`.github/workflows/${trustedList ? 'wiki-trusted-data.yml' : 'wiki-quality.yml'}`,head_sha:head,status:'completed',conclusion:'success',created_at:'2026-01-01T00:00:00Z',run_started_at:'2026-01-01T00:00:00Z',pull_requests:[{number:37}]}]}
        : url.includes('/actions/workflows/') ? {id:42,state:'active',path:'.github/workflows/wiki-trusted-data.yml'}
        : m.params.request.url.endsWith('/actions/runs/2') ? {id:2,workflow_id:42,repository:{id:1},run_attempt:1,event:'pull_request_target',status:'completed',conclusion:'success',head_sha:head,path:'.github/workflows/wiki-trusted-data.yml',pull_requests:[{number:37,head:{sha:head,repo:{id:1}},base:{sha:base,repo:{id:1}}}]}
        : m.params.request.url.includes('/actions/runs/')
          ? {id:1,run_attempt:1,event:'pull_request', conclusion:'success',head_sha:head,path:'.github/workflows/wiki-quality.yml',pull_requests:[{number:37,head:{sha:head},base:{sha:base}}]}
        : {state:'open',head:{sha:stale ? 'c'.repeat(40) : head,repo:{id:1}},base:{sha:base,repo:{id:1}}};
      send('Fetch.fulfillRequest',{requestId:m.params.requestId,responseCode:200,responseHeaders:[{name:'Content-Type',value:'application/json'},{name:'Access-Control-Allow-Origin',value:'*'}],body:Buffer.from(JSON.stringify(data)).toString('base64')},m.sessionId).catch(() => {});
    }
  };
  const target=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId:target.targetId,flatten:true});
  const cdp=(method,params={})=>send(method,params,sessionId);
  await cdp('Page.enable'); await cdp('Runtime.enable');
  await cdp('Page.addScriptToEvaluateOnNewDocument', {source: `if (window === top) { window.testEvents = []; addEventListener('securitypolicyviolation', e => window.testEvents.push({type:'test:csp', blocked:e.blockedURI, directive:e.violatedDirective})); addEventListener('message', e => { if (e.data?.type?.startsWith('test:')) window.testEvents.push(e.data); }); }`});
  await cdp('Fetch.enable',{patterns:[{urlPattern:'https://api.github.com/*'}]});
  const evaluate=async (expression, contextId) => {
    const reply=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,...(contextId ? {contextId} : {})});
    if(reply.exceptionDetails) throw new Error(JSON.stringify(reply.exceptionDetails));
    return reply.result.value;
  };
  await cdp('Page.navigate',{url:`http://127.0.0.1:${server.address().port}/?pr=37`});
  let events = [];
  for (let i=0;i<100;i++) {
    await wait(100);
    try { events = await evaluate('window.testEvents || []'); if (events.some(e => e.type === 'test:next')) break; } catch {}
  }
  const outer=await evaluate("({review:document.querySelector('#review-label').textContent,notice:document.querySelector('.copyright').textContent,visible:!document.querySelector('#preview').hidden,status:document.querySelector('#status').textContent})");
  const home = events.find(e => e.type === 'test:home');
  const next = events.find(e => e.type === 'test:next');
  if (!home?.search || !Number(home.count) || !next?.prose || !next?.image || !next?.css) throw new Error('Real Wiki search, assets or navigation failed: ' + JSON.stringify({events,outer}));
  if (outer.review !== '未经人工审查' || !outer.notice.includes('非官方') || !outer.visible || canaries) throw new Error('Preview notice or request failed');
  stale = true;
  await evaluate("document.dispatchEvent(new Event('visibilitychange'))");
  let hidden = false;
  for (let i=0;i<100;i++) {
    await wait(100);
    if (await evaluate("document.querySelector('#preview').hidden")) { hidden = true; break; }
  }
  if (!hidden) throw new Error('Stale preview remained visible');
  console.log('PASS: actual Wiki search, stats, article navigation and stale preview');
} finally {
  socket?.close(); browser.kill(); server.close(); await wait(250);
  await rm(profile,{recursive:true,force:true,maxRetries:5,retryDelay:200});
}
