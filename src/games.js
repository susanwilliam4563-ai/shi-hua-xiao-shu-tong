const unique=items=>[...new Set(items)];
const rotate=(items,offset)=>items.map((_,i)=>items[(i+offset)%items.length]);

export const gameModes=[
  {id:'mixed',title:'诗词大闯关',desc:'八种玩法轮流出现，适合每天挑战',icon:'闯'},
  {id:'title',title:'看图猜诗',desc:'看意象线索，找出藏在画里的诗',icon:'画'},
  {id:'next',title:'上下句连线',desc:'读上句，接住正确的下句',icon:'接'},
  {id:'typo',title:'错字侦探',desc:'找出偷偷换掉字的诗句',icon:'辨'},
  {id:'season',title:'季节分类',desc:'把诗送回它的季节篮子',icon:'时'},
  {id:'order',title:'诗句排序',desc:'沿着画面路线排好整首诗',icon:'序'},
  {id:'blank',title:'关键词填空',desc:'找回藏起来的意象词',icon:'填'},
  {id:'author',title:'诗人与作品',desc:'帮诗找到它的作者',icon:'人'},
  {id:'theme',title:'主题小侦探',desc:'辨认山水、思乡与童趣',icon:'意'}
];

function distractPoems(poems,poem,field,count=3){return unique(rotate(poems,poems.indexOf(poem)+1).filter(p=>p[field]!==poem[field]).map(p=>p[field])).slice(0,count)}
function makeTypo(line){const swaps=[['月','日'],['山','水'],['花','草'],['风','云'],['白','百'],['春','秋'],['天','田'],['鸟','马']];for(const [a,b] of swaps)if(line.includes(a))return line.replace(a,b);return line.slice(0,-1)+'木'}
export function blankForPoem(poem,index=0){const lineIndex=index%poem.lines.length,line=poem.lines[lineIndex],mode=index%5;if(mode===3||mode===4){const before=poem.lines[(lineIndex-1+poem.lines.length)%poem.lines.length],options=unique([line,...rotate(poem.lines,lineIndex+1)]).slice(0,4);return {kind:mode===3?'整句回忆':'看上句接下句',line,word:line,masked:mode===3?'＿＿＿＿＿＿':`${before} / ＿＿＿＿＿＿`,options}}
 let word=poem.imagery.find(x=>line.includes(x));if(!word){const start=mode===0?0:mode===1?Math.max(0,line.length-2):Math.max(1,Math.floor(line.length/2)-1),size=mode===2?3:2;word=line.slice(start,start+size)}const other=poem.lines.map((x,i)=>x.slice((i+mode)%Math.max(1,x.length-1),(i+mode)%Math.max(1,x.length-1)+Math.max(2,word.length)));const pool=unique([word,...poem.imagery.filter(x=>x!==word),...other.filter(x=>x&&x!==word)]).slice(0,4);return {kind:['开头提示','句尾提示','诗中词语'][mode],line,word,masked:line.replace(word,'＿'.repeat(word.length)),options:pool}}

export function createQuestion(type,poem,poems,index=0){
  const lineIndex=index%3,line=poem.lines[lineIndex],next=poem.lines[lineIndex+1];
  if(type==='title')return {type,poemId:poem.id,prompt:`画面里有“${poem.imagery.join('、')}”，是哪首诗？`,answer:poem.title,options:unique([poem.title,...distractPoems(poems,poem,'title')]),tip:'先把几个意象连成一幅画。'};
  if(type==='next')return {type,poemId:poem.id,prompt:`“${line}”的下一句是？`,answer:next,options:unique([next,...poem.lines.filter(x=>x!==next).slice(0,3)]),tip:'沿着诗里的画面往下走。'};
  if(type==='typo'){const wrong=makeTypo(line);return {type,poemId:poem.id,prompt:'哪一句写得完全正确？',answer:line,options:unique([wrong,line,...poem.lines.filter(x=>x!==line).slice(0,2)]),tip:'慢慢读，看看哪个字让画面变了。'}}
  if(type==='season')return {type,poemId:poem.id,prompt:`《${poem.title}》最适合放进哪个季节篮子？`,answer:poem.season,options:['春','夏','秋','冬'],tip:'找一找诗里的天气、花草和颜色。'};
  if(type==='order')return {type,poemId:poem.id,prompt:'依次点击，把诗句排回正确顺序',answer:poem.lines.join('|'),options:rotate(poem.lines,2),tip:`第一句是“${poem.lines[0]}”。`};
  if(type==='blank'){const blank=blankForPoem(poem,index);return {type,poemId:poem.id,prompt:`${blank.masked}，空白处是什么？`,answer:blank.word,options:blank.options,tip:'轻声读完整句，再从词语卡里选择。'}}
  if(type==='author')return {type,poemId:poem.id,prompt:`《${poem.title}》的作者是谁？`,answer:poem.author,options:unique([poem.author,...distractPoems(poems,poem,'author')]),tip:'想想诗名旁边见过的诗人。'};
  return {type:'theme',poemId:poem.id,prompt:`《${poem.title}》主要写的是哪类画面或心情？`,answer:poem.theme,options:unique([poem.theme,...distractPoems(poems,poem,'theme')]),tip:'先说说诗里发生了什么。'};
}

export function createGameRound(mode,poems,count=8,seed=0){
  const types=mode==='mixed'?gameModes.slice(1).map(x=>x.id):Array(count).fill(mode);
  return Array.from({length:count},(_,i)=>createQuestion(types[i%types.length],poems[(seed+i)%poems.length],poems,i));
}

export function pointsForAnswer(correct,attempt=1){return correct?(attempt===1?10:6):0}
export function levelForPoints(points){if(points>=500)return {name:'诗林小先生',icon:'🌳'};if(points>=250)return {name:'花开小诗人',icon:'🌸'};if(points>=100)return {name:'青枝小书童',icon:'🌿'};return {name:'新芽小书童',icon:'🌱'}}
