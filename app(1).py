#!/usr/bin/env python3
"""FileConverter - one-file Python web app. No third-party packages required."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
import os

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#101827">
<title>FileConverter</title>
<style>
:root{color-scheme:dark;--bg:#0b1220;--panel:#142238;--line:#2b405c;--text:#edf4ff;--muted:#9fb1c9;--mint:#72e0c0}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 85% 0,#203c59,transparent 35%),var(--bg);color:var(--text);font:16px system-ui,sans-serif}
header{max-width:900px;margin:auto;padding:22px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ffffff18}
.brand{display:flex;align-items:center;gap:12px;font-weight:800}.logo{display:grid;place-items:center;width:42px;height:42px;border-radius:13px;background:var(--mint);color:#082018}
small,.muted{color:var(--muted)}main{max-width:850px;margin:48px auto;padding:0 20px}.tag{font-size:12px;letter-spacing:3px;color:var(--mint);font-weight:800}
h1{font-size:clamp(38px,8vw,62px);line-height:1.05;margin:12px 0}h1 span{color:var(--mint)}
.panel{background:#142238eF;border:1px solid var(--line);border-radius:22px;padding:22px;margin-top:28px}
.drop{display:flex;flex-direction:column;align-items:center;gap:9px;padding:28px 12px;border:1px dashed #607b99;border-radius:16px;cursor:pointer}
.plus{font-size:30px;color:var(--mint)}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
button,select{border:1px solid var(--line);border-radius:12px;padding:13px 16px;background:#1b2a42;color:var(--text);font:inherit}
button{background:var(--mint);color:#082018;font-weight:800;cursor:pointer;flex:1}.secondary{background:#1b2a42;color:var(--text)}
label.field{display:block;color:var(--muted);font-size:13px;margin:14px 0 7px}select{width:100%}
#result{white-space:pre-wrap;overflow-wrap:anywhere;background:#09111e;border:1px solid var(--line);border-radius:12px;padding:16px;margin-top:16px;min-height:78px;color:#cce5df;font-size:13px}
.features{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-top:16px}
.features article{padding:16px;border:1px solid var(--line);border-radius:15px;background:#ffffff06}
.features p{font-size:13px;color:var(--muted);line-height:1.5}footer{text-align:center;color:#71839c;padding:28px;font-size:12px}
@media(max-width:520px){main{margin:30px auto}.panel{padding:15px}.actions button{flex-basis:100%}}
</style></head>
<body>
<header><div class="brand"><span class="logo">FC</span><div>FileConverter<br><small>Simple · Private · Fast</small></div></div><small>VERSION 1.0</small></header>
<main>
<p class="tag">YOUR FILE TOOLKIT</p>
<h1>Work with files.<br><span>Keep it simple.</span></h1>
<p class="muted">Inspect files, calculate SHA-256, and convert supported text formats. Files are processed in your browser and are not uploaded to this server.</p>
<section class="panel">
<label class="drop" for="file"><span class="plus">＋</span><b>Choose a file</b><small id="filename">No file selected</small></label>
<input id="file" type="file" hidden>
<div class="actions"><button class="secondary" id="analyze">Analyze file</button><button id="convert">Convert file</button></div>
<label class="field" for="kind">Conversion type</label>
<select id="kind"><option value="txt">TXT → HTML</option><option value="csv">CSV → JSON</option><option value="json">Format JSON</option></select>
<div id="result" aria-live="polite">Your results will appear here.</div>
</section>
<section class="features">
<article><b>Private processing</b><p>Your selected file stays in this browser.</p></article>
<article><b>File information</b><p>Basic signature detection, file size and SHA-256.</p></article>
<article><b>Supported formats</b><p>TXT, simple CSV and JSON conversions.</p></article>
</section>
</main><footer>FileConverter · Built with Python</footer>
<script>
const $=id=>document.getElementById(id);let chosen=null;
$('file').addEventListener('change',e=>{chosen=e.target.files[0]||null;$('filename').textContent=chosen?chosen.name+' · '+size(chosen.size):'No file selected'});
function size(n){return n<1024?n+' B':n<1048576?(n/1024).toFixed(1)+' KB':(n/1048576).toFixed(2)+' MB'}
function show(s){$('result').textContent=s}
function signature(b){let h=[...b.slice(0,8)].map(x=>x.toString(16).padStart(2,'0')).join('').toUpperCase();if(h.startsWith('4D5A'))return 'Windows executable (MZ)';if(h.startsWith('7F454C46'))return 'ELF executable';if(h.startsWith('89504E470D0A1A0A'))return 'PNG image';if(h.startsWith('FFD8FF'))return 'JPEG image';if(h.startsWith('504B0304'))return 'ZIP-based file (possibly APK)';return 'Unknown / plain data'}
$('analyze').onclick=async()=>{if(!chosen)return show('Choose a file first.');try{let b=await chosen.arrayBuffer(),hash=await crypto.subtle.digest('SHA-256',b),sha=[...new Uint8Array(hash)].map(x=>x.toString(16).padStart(2,'0')).join('');show('Name: '+chosen.name+'\\nSize: '+size(chosen.size)+'\\nDetected: '+signature(new Uint8Array(b))+'\\nSHA-256: '+sha+'\\n\\nBasic signature check only; not a full malware scan.')}catch(e){show('Analysis failed: '+e.message)}};
function download(name,data,type){let a=document.createElement('a'),u=URL.createObjectURL(new Blob([data],{type}));a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1200)}
function esc(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
$('convert').onclick=async()=>{if(!chosen)return show('Choose a file first.');try{let t=await chosen.text(),k=$('kind').value,out,name,type,base=chosen.name.replace(/\\.[^.]+$/,'');if(k==='txt'){out='<!doctype html><meta charset="utf-8"><title>'+esc(chosen.name)+'</title><pre>'+esc(t)+'</pre>';name=base+'.html';type='text/html'}else if(k==='csv'){let rows=t.trim().split(/\\r?\\n/).map(x=>x.split(','));if(rows.length<2)throw Error('CSV needs a header and at least one row.');let heads=rows.shift().map(x=>x.trim());out=JSON.stringify(rows.map(r=>Object.fromEntries(heads.map((h,i)=>[h,(r[i]||'').trim()]))),null,2);name=base+'.json';type='application/json'}else{out=JSON.stringify(JSON.parse(t),null,2);name=base+'.formatted.json';type='application/json'}download(name,out,type);show('Conversion complete. Check your Downloads folder.')}catch(e){show('Conversion failed: '+e.message)}};
</script></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"FileConverter listening on 0.0.0.0:{port}")
    server.serve_forever()
