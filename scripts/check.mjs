import fs from 'node:fs';import path from 'node:path';
const root=process.cwd(),files=['index.html','src/app.js','src/poems.js','src/terms.js','src/review.js','src/games.js','src/storage.js','src/styles.css','src/rewards.css','src/corrections.css','src/reading.css','src/v8.css','src/semantic-fixes.css','public/manifest.webmanifest','public/sw.js'];let bad=[];
for(const f of files){if(!fs.existsSync(path.join(root,f)))bad.push(`缺少 ${f}`)}
const app=fs.readFileSync(path.join(root,'src/app.js'),'utf8');if(/\bany\b/.test(app))bad.push('发现 any');if((app.match(/console\./g)||[]).length)bad.push('发现 console');
if(bad.length){console.error(bad.join('\n'));process.exit(1)}console.log(`检查通过：${files.length} 个核心文件`);
