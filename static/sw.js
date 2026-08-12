/* 2026-08-12: 专利档案库 Service Worker — 二次访问秒开。
   策略: 静态资源(css/js/webp/index.json) cache-first + 后台更新(SWR);
   页面/HTML network-first, 离线 fallback 缓存。 */
const CACHE = 'patent-site-v1';
const SWR = /\.(css|js|webp|png|jpe?g|woff2?)(\?|$)|index\.json$/;

self.addEventListener('install', () => {
    self.skipWaiting();
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (e) => {
    const url = new URL(e.request.url);
    if (e.request.method !== 'GET' || url.origin !== location.origin) return;

    if (SWR.test(url.pathname)) {
        // 静态资源: 有缓存先返回(秒开), 后台拉新更新缓存
        e.respondWith(
            caches.match(e.request).then((cached) => {
                const fetched = fetch(e.request)
                    .then((res) => {
                        if (res && res.ok) {
                            const clone = res.clone();
                            caches.open(CACHE).then((c) => c.put(e.request, clone));
                        }
                        return res;
                    })
                    .catch(() => cached);
                return cached || fetched;
            })
        );
        return;
    }

    // 页面: 网络优先, 失败(离线/弱网)回退缓存
    e.respondWith(
        fetch(e.request)
            .then((res) => {
                if (res && res.ok) {
                    const clone = res.clone();
                    caches.open(CACHE).then((c) => c.put(e.request, clone));
                }
                return res;
            })
            .catch(() => caches.match(e.request))
    );
});
