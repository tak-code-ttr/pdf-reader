// オフライン用 Service Worker。CACHE の値は build.py がビルドごとに書き換える（変わると新しい版に更新される）
const CACHE = 'pdf-reader-141e535330aa';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('pdf-reader-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
// キャッシュ優先（オフラインでも即起動）。更新は sw.js の変化で検知する
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => hit || fetch(req)));
});
