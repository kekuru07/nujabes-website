const CACHE_NAME = "fantasy-football-cache-v1";
const urlsToCache = [
    "/",
    "/static/css/homepage.css",
    "/static/css/albumpage.css",
    "/static/css/discography.css",
    "/static/css/accessibility.css",
    "/static/images/favicon.jpg",
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(urlsToCache).catch((err) => {
                console.error('Failed to cache assets:', err);
            });
        })
    );
});

self.addEventListener("fetch", (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request).catch((err) => {
                console.error('Fetch failed; returning offline page:', err);
                return caches.match('/offline.html'); // You can replace this with an offline fallback page if you want
            });
        })
    );
});
