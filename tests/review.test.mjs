import test from 'node:test';import assert from 'node:assert/strict';import {scheduleReview,taskPriority,createDailyTasks,DAY} from '../src/review.js';import {poems} from '../src/poems.js';
test('答对后提升掌握等级并安排更晚复习',()=>{let now=1000,p=scheduleReview({level:2,intervalDays:2},{correct:true,hints:0},now);assert.equal(p.level,3);assert.equal(p.nextReviewAt,now+7*DAY)});
test('答错或提示过多会缩短间隔',()=>{let p=scheduleReview({level:4,intervalDays:14},{correct:false,hints:3},0);assert.equal(p.level,3);assert.equal(p.intervalDays,7)});
test('到期任务优先于新诗',()=>{let now=Date.now();assert.ok(taskPriority(poems[0],{nextReviewAt:now-1},now)>taskPriority(poems[1],{},now))});
test('每日任务数可配置且诗词不重复',()=>{let tasks=createDailyTasks(poems,{},5,0);assert.equal(tasks.length,5);assert.equal(new Set(tasks.map(x=>x.poemId)).size,5)});
test('内容至少 25 首且字段完整',()=>{assert.ok(poems.length>=25);for(const p of poems){assert.ok(p.lines.length>=4);assert.equal(p.pinyin.length,p.lines.length);assert.equal(p.explanations.length,p.lines.length);assert.ok(p.questions.length>=4)}});
test('成都一至三年级上册清单完整覆盖',()=>{const expected=['江南','画','咏鹅','悯农（其二）','古朗月行（节选）','风','登鹳雀楼','望庐山瀑布','梅花','小儿垂钓','江雪','夜宿山寺','敕勒歌','山行','赠刘景文','夜书所见','望天门山','饮湖上初晴后雨','望洞庭'];const upper=poems.filter(p=>p.semester==='上').map(p=>p.title);for(const title of expected)assert.ok(upper.includes(title),`缺少 ${title}`)});
