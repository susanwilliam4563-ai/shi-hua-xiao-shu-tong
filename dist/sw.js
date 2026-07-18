const VERSION='poem-scholar-v29';
const POEMS=['jiang-nan','hua','yong-e','min-nong-er','gu-lang-yue-xing','feng','jing-ye-si','chun-xiao','cun-ju','xiao-chi','mei-hua','xiao-er-chui-diao','jiang-xue','ye-su-shan-si','chi-le-ge','deng-guan-que-lou','wang-lu-shan-pu-bu','jue-ju','fu-de-gu-yuan-cao','shan-xing','zeng-liu-jing-wen','ye-shu-suo-jian','wang-tian-men-shan','yin-hu-shang','wang-dong-ting'];
const CORE=['/','/index.html','/manifest.webmanifest','/assets/app.js?v=29','/assets/poems.js?v=29','/assets/terms.js?v=29','/assets/review.js?v=29','/assets/games.js?v=29','/assets/storage.js?v=29','/assets/adventure.js?v=29','/assets/styles.css?v=29','/assets/rewards.css?v=29','/assets/corrections.css?v=29','/assets/reading.css?v=29','/assets/v8.css?v=29','/assets/semantic-fixes.css?v=29','/assets/adventure.css?v=29','/images/app-icon.png','/images/app-icon-512.png'];
const IMAGES=POEMS.map(id=>`/images/${id}.webp?v=29`);
self.addEventListener('install',event=>event.waitUntil(caches.open(VERSION).then(async cache=>{
  await cache.addAll(CORE);
  await Promise.allSettled(IMAGES.map(url=>cache.add(url)));
}).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==VERSION).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  if(event.request.mode==='navigate'){
    event.respondWith(fetch(event.request).then(async response=>{
      if(response.ok){
        const cache=await caches.open(VERSION);
        await cache.put('/',response.clone());
      }
      return response;
    }).catch(async()=>await caches.match('/')||await caches.match('/index.html')));
    return;
  }
  event.respondWith(caches.match(event.request).then(hit=>hit||fetch(event.request).then(async response=>{
    if(response.ok&&new URL(event.request.url).origin===self.location.origin){
      const cache=await caches.open(VERSION);
      await cache.put(event.request,response.clone());
    }
    return response;
  }).catch(()=>new Response('离线时暂不可用',{status:503,headers:{'Content-Type':'text/plain; charset=utf-8'}}))));
});
