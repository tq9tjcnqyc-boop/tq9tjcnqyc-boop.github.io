#!/usr/bin/env python3
"""电脑视口截图, 看图片实际显示"""
import json, subprocess, time, sys, base64

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9463

proc = subprocess.Popen([
    CHROME, "--headless=new", "--disable-gpu", "--disable-extensions",
    f"--remote-debugging-port={PORT}",
    "--user-data-dir=/tmp/pf-shot",
    "--window-size=1200,1000",
    "https://tq9tjcnqyc-boop.github.io/posts/20260811033000-patent-008/?v=20"
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
    time.sleep(4)
    # 滚动到第一张图 (摘要附图) 位置
    ev("""
        (function(){
            var img = document.querySelector('.post-content img');
            if (img) img.scrollIntoView({block: 'center'});
            return true;
        })()
    """)
    time.sleep(2)
    # 截图
    r = rpc("Page.captureScreenshot", {"format": "png"})
    data = r.get("result", {}).get("data")
    if data:
        with open('/tmp/patent-008-screenshot.png', 'wb') as f:
            f.write(base64.b64decode(data))
        print("截图已保存: /tmp/patent-008-screenshot.png")
    # 图片信息
    info = ev("""
        (function(){
            var im = document.querySelector('.post-content img');
            if (!im) return null;
            return {
                naturalW: im.naturalWidth, naturalH: im.naturalHeight,
                rectW: Math.round(im.getBoundingClientRect().width),
                rectH: Math.round(im.getBoundingClientRect().height),
                src: im.src.slice(0, 70)
            };
        })()
    """)
    print("第一张图:", json.dumps(info, ensure_ascii=False))
    ws.close()
finally:
    proc.terminate()
