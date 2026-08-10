#!/usr/bin/env python3
"""线上 MPP 页面: 每张图下载+解码验证, 确认是否残缺"""
import json, subprocess, time, sys, base64, os

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9464

proc = subprocess.Popen([
    CHROME, "--headless=new", "--disable-gpu", "--disable-extensions",
    f"--remote-debugging-port={PORT}",
    "--user-data-dir=/tmp/pf-verify",
    "--window-size=1200,1000",
    "https://tq9tjcnqyc-boop.github.io/posts/20260811000000-mpp/?v=22"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

try:
    import urllib.request
    d = None
    for _ in range(30):
        try:
            d = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=2))
            target = [t for t in d if "github.io" in t.get("url", "")]
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

    for _ in range(100):
        if ev("document.readyState === 'complete'"):
            break
        time.sleep(0.2)
    time.sleep(5)
    r = ev("""
        (function(){
            var out = [];
            document.querySelectorAll('.post-content img').forEach(function(im){
                out.push({
                    alt: im.alt.slice(0, 10),
                    src: im.currentSrc || im.src,
                    complete: im.complete,
                    naturalW: im.naturalWidth,
                    rectW: Math.round(im.getBoundingClientRect().width)
                });
            });
            return out;
        })()
    """)
    print("页面图片列表:")
    for x in r:
        print(f"  {x['alt']}: complete={x['complete']} natural={x['naturalW']} src={x['src'].split('/')[-1]}")
    ws.close()
finally:
    proc.terminate()
