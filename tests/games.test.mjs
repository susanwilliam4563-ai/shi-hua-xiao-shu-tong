import test from 'node:test';import assert from 'node:assert/strict';import {createGameRound,createQuestion,gameModes,pointsForAnswer,levelForPoints,blankForPoem} from '../src/games.js';import {poems} from '../src/poems.js';
test('游戏馆包含综合模式和八种专项玩法',()=>{assert.equal(gameModes.length,9);assert.equal(new Set(gameModes.map(x=>x.id)).size,9)});
test('综合闯关生成八道不同玩法题',()=>{let round=createGameRound('mixed',poems,8,0);assert.equal(round.length,8);assert.equal(new Set(round.map(x=>x.type)).size,8)});
test('选择型题目的正确答案都在选项中',()=>{for(const mode of gameModes.slice(1).filter(x=>x.id!=='order')){let q=createQuestion(mode.id,poems[0],poems,0);assert.ok(q.options.includes(q.answer),mode.id)}});
test('积分奖励鼓励首次答对但保留重试成长',()=>{assert.equal(pointsForAnswer(true,1),10);assert.equal(pointsForAnswer(true,2),6);assert.equal(pointsForAnswer(false,1),0)});
test('积分等级按成长节点提升',()=>{assert.equal(levelForPoints(0).name,'新芽小书童');assert.equal(levelForPoints(250).name,'花开小诗人');assert.equal(levelForPoints(500).name,'诗林小先生')});
test('全部诗词都能生成可点击填空卡',()=>{for(const poem of poems)for(let i=0;i<poem.lines.length;i++){let blank=blankForPoem(poem,i);assert.ok(blank.word);assert.ok(blank.masked.includes('＿＿'),`${poem.title} 第${i+1}句未挖空`);assert.ok(blank.options.includes(blank.word));assert.ok(blank.options.length>=2)}});
test('排序题提供独立诗句而不是伪装成选择题',()=>{for(const poem of poems){let q=createQuestion('order',poem,poems);assert.equal(q.options.length,poem.lines.length);assert.equal(q.answer.split('|').length,poem.lines.length);assert.deepEqual(new Set(q.options),new Set(poem.lines))}});
