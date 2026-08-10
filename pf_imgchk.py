#!/usr/bin/env python3
"""检查文章图片渲染: 尺寸/容器/居中"""
import json, subprocess, time, sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9452

proc = subprocess.Popen([
    CHROME, "--headless=new", "--disable-gpu", "--disable-extensions",
    f"--remote-debugging-port={PORT}",
    "--user-data-dir=/tmp/pf-img",
    "--window-size=566,900",
    "http://127.0.0.1:8899/posts/20260811000000-mpp/"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    import urllib.request
    d = None
    for _ in range(30):
        try:
            d = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=2))
            target = [t for t in d if "8899" in t.get("url", "")]
            if target:
                d = target
                break
        except Exception:
            time.sleep(1)
    if not d:
        print("NO TARGET"); sys.exit(1)

    import websocket
    time.sleep(1)
    ws = websocket.create_connection(d[0]["webSocketDebuggerUrl"], timeout=20, suppress_origin=True)
    mid = [0]
    def rpc(method, params=None):
        mid[0] += 1
        ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid[0]:
                return msg
    def ev(expr):
        r = rpc("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        return r.get("result", {}).get("result", {}).get("value")

    for _ in range(80):
        if ev("document.readyState === 'complete'"):
            break
        time.sleep(0.1)
    time.sleep(3)  # 等图片加载
    ev("window.scrollTo(0, document.body.scrollHeight)")  # 触发 lazy 加载
    time.sleep(2)
    r = ev("""
        (function(){
            var out = [];
            document.querySelectorAll('.post-content p').forEach(function(p){
                var img = p.querySelector('img');
                if (img) {
                    var pr = p.getBoundingClientRect();
                    var ir = img.getBoundingClientRect();
                    var cs = getComputedStyle(img);
                    out.push({
                        alt: img.alt.slice(0, 12),
                        imgW: Math.round(ir.width), imgH: Math.round(ir.height),
                        naturalW: img.naturalWidth, complete: img.complete,
                        pW: Math.round(pr.width),
                        pAlign: getComputedStyle(p).textAlign,
                        imgDisplay: cs.display,
                        imgMaxW: cs.maxWidth,
                        imgStyle: img.getAttribute('style') || ''
                    });
                }
            });
            // 容器
            var article = document.querySelector('.post-content');
            return {
                imgs: out,
                containerW: article ? Math.round(article.getBoundingClientRect().width) : null
            };
        })()
    """)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    ws.close()
finally:
    proc.terminate()
