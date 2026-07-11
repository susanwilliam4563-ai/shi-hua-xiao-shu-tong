import test from 'node:test';import assert from 'node:assert/strict';import {scheduleReview,taskPriority,createDailyTasks,DAY} from '../src/review.js';import {poems} from '../src/poems.js';
test('答对后提升掌握等级并安排更晚复习',()=>{let now=1000,p=scheduleReview({level:2,intervalDays:2},{correct:true,hints:0},now);assert.equal(p.level,3);assert.equal(p.nextReviewAt,now+7*DAY)});
test('答错或提示过多会缩短间隔',()=>{let p=scheduleReview({level:4,intervalDays:14},{correct:false,hints:3},0);assert.equal(p.level,3);assert.equal(p.intervalDays,7)});
test('到期任务优先于新诗',()=>{let now=Date.now();assert.ok(taskPriority(poems[0],{nextReviewAt:now-1},now)>taskPriority(poems[1],{},now))});
test('每日任务数可配置且诗词不重复',()=>{let tasks=createDailyTasks(poems,{},5,0);assert.equal(tasks.length,5);assert.equal(new Set(tasks.map(x=>x.poemId)).size,5)});
test('内容至少 12 首且字段完整',()=>{assert.ok(poems.length>=12);for(const p of poems){assert.equal(p.lines.length,4);assert.equal(p.pinyin.length,4);assert.equal(p.explanations.length,4);assert.ok(p.questions.length>=4)}});
