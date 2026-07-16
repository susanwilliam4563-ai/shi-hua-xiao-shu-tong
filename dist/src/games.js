const unique=items=>[...new Set(items)];
const rotate=(items,offset)=>items.map((_,i)=>items[(i+offset)%items.length]);
const sourceOnlyIds=new Set(['hua','jiang-nan','chi-le-ge']);
const unclearSeasonIds=new Set(['hua','feng','yong-e','gu-lang-yue-xing','jing-ye-si','xiao-er-chui-diao','ye-su-shan-si','deng-guan-que-lou','wang-lu-shan-pu-bu','wang-tian-men-shan']);

export const gameModes=[
  {id:'mixed',title:'今日随机冒险',desc:'每次遇见不同玩法，不会一直做同一种题',icon:'闯'},
  {id:'title',title:'看图猜诗',desc:'看意象线索，找出藏在画里的诗',icon:'画'},
  {id:'next',title:'诗句连线',desc:'读上句，接住正确的下句',icon:'接'},
  {id:'typo',title:'错字侦探',desc:'找出偷偷换掉字的诗句',icon:'辨'},
  {id:'season',title:'时间地点配对',desc:'把诗送回正确的季节和场景',icon:'时'},
  {id:'order',title:'诗句排序',desc:'沿着画面路线排好整首诗',icon:'序'},
  {id:'blank',title:'补回缺失字',desc:'帮错字精灵送回关键字',icon:'填'},
  {id:'scene',title:'诗句找画面',desc:'读诗句，选出最符合的画面',icon:'景'},
  {id:'same',title:'句子找伙伴',desc:'从多首诗中找出同一首诗的句子',icon:'伴'},
  {id:'puzzle',title:'诗词拼图',desc:'把四句诗拼成完整画卷',icon:'拼'},
  {id:'timed',title:'限时找景物',desc:'快速找到诗中真正出现的景物',icon:'寻'},
  {id:'poet',title:'诗人角色问答',desc:'听诗仙信使讲线索，猜猜是哪位诗人',icon:'问'},
  {id:'emotion',title:'诗词心情盒',desc:'给古诗选择合适的情绪',icon:'心'},
  {id:'identity',title:'诗名作者挑战',desc:'根据画面说出诗名和作者',icon:'名'},
  {id:'theme',title:'诗里藏着什么',desc:'辨认山水、思乡与童趣',icon:'意'}
];

function distractPoems(poems,poem,field,count=3){return unique(rotate(poems,poems.indexOf(poem)+1).filter(p=>p[field]!==poem[field]).map(p=>p[field])).slice(0,count)}
function makeTypo(line){const swaps=[['月','日'],['山','水'],['花','草'],['风','云'],['白','百'],['春','秋'],['天','田'],['鸟','马']];for(const [a,b] of swaps)if(line.includes(a))return line.replace(a,b);return line.slice(0,-1)+'木'}
export function blankForPoem(poem,index=0){const lineIndex=index%poem.lines.length,line=poem.lines[lineIndex],mode=index%6;if(mode===3||mode===4){const before=poem.lines[(lineIndex-1+poem.lines.length)%poem.lines.length],options=unique([line,...rotate(poem.lines,lineIndex+1)]).slice(0,4);return {kind:mode===3?'整句回忆':'上下句接龙',instruction:mode===3?'不看提示，找回完整诗句。':'读上句，找到画面自然接下去的诗句。',line,word:line,masked:mode===3?'整句藏起来了：＿＿＿＿＿＿':`${before} / ＿＿＿＿＿＿`,options}}
 if(mode===5){const options=unique([line,makeTypo(line),...rotate(poem.lines,lineIndex+1)]).slice(0,4);return {kind:'辨认错字',instruction:'逐字读，选出没有被偷偷换字的诗句。',line,word:line,masked:'哪一句完全正确？＿＿＿＿',options}}
 const start=mode===0?0:mode===1?Math.max(0,line.length-2):Math.max(1,Math.floor(line.length/2)-1),size=mode===2?Math.min(3,line.length-start):Math.min(2,line.length-start);let word=mode===2?poem.imagery.find(x=>line.includes(x)):null;if(!word)word=line.slice(start,start+size);const other=poem.lines.map((x,i)=>x.slice((i+mode)%Math.max(1,x.length-1),(i+mode)%Math.max(1,x.length-1)+Math.max(2,word.length)));const pool=unique([word,...poem.imagery.filter(x=>x!==word),...other.filter(x=>x&&x!==word)]).slice(0,4);const kinds=['句首认字','句尾补词','诗中词语'];const instructions=['认出诗句开头缺少的字词。','读到句尾，补回最后的字词。','找到藏在诗句中间的意象词。'];return {kind:kinds[mode],instruction:instructions[mode],line,word,masked:line.replace(word,'＿'.repeat(word.length)),options:pool}}

export function createQuestion(type,poem,poems,index=0){
  if((type==='author'||type==='poet'||type==='identity')&&sourceOnlyIds.has(poem.id))type='title';
  if(type==='season'&&unclearSeasonIds.has(poem.id))type='theme';
  const lineIndex=index%3,line=poem.lines[lineIndex],next=poem.lines[lineIndex+1];
  if(type==='title')return {type,poemId:poem.id,prompt:`画面里有“${poem.imagery.join('、')}”，是哪首诗？`,answer:poem.title,options:unique([poem.title,...distractPoems(poems,poem,'title')]),tip:'先把几个意象连成一幅画。'};
  if(type==='next')return {type,poemId:poem.id,prompt:`“${line}”的下一句是？`,answer:next,options:unique([next,...poem.lines.filter(x=>x!==next).slice(0,3)]),tip:'沿着诗里的画面往下走。'};
  if(type==='typo'){const wrong=makeTypo(line);return {type,poemId:poem.id,prompt:'哪一句写得完全正确？',answer:line,options:unique([wrong,line,...poem.lines.filter(x=>x!==line).slice(0,2)]),tip:'慢慢读，看看哪个字让画面变了。'}}
  if(type==='season')return {type,poemId:poem.id,prompt:`《${poem.title}》最适合放进哪个季节篮子？`,answer:poem.season,options:['春','夏','秋','冬'],tip:'找一找诗里的天气、花草和颜色。'};
  if(type==='order'||type==='puzzle')return {type,poemId:poem.id,prompt:type==='puzzle'?'拼好诗句，修复这幅诗词画卷':'依次点击，把诗句排回正确顺序',answer:poem.lines.join('|'),options:rotate(poem.lines,2),tip:`第一句是“${poem.lines[0]}”。`};
  if(type==='blank'){const blank=blankForPoem(poem,index);return {type,poemId:poem.id,prompt:`${blank.masked}，空白处是什么？`,answer:blank.word,options:blank.options,tip:'轻声读完整句，再从词语卡里选择。'}}
  if(type==='author')return {type,poemId:poem.id,prompt:`《${poem.title}》的作者是谁？`,answer:poem.author,options:unique([poem.author,...distractPoems(poems,poem,'author')]),tip:'想想诗名旁边见过的诗人。'};
  if(type==='scene')return {type,poemId:poem.id,prompt:`哪幅画最像“${line}”？`,answer:poem.id,options:unique([poem.id,...rotate(poems,poems.indexOf(poem)+1).slice(0,3).map(p=>p.id)]),tip:`诗句里藏着“${poem.imagery[lineIndex]||poem.imagery[0]}”。`,visual:true};
  if(type==='same'){const other=rotate(poems,poems.indexOf(poem)+1).filter(p=>p.id!==poem.id).slice(0,3);return {type,poemId:poem.id,prompt:`哪一句也属于《${poem.title}》？`,answer:next,options:unique([next,...other.map(p=>p.lines[index%p.lines.length])]),tip:'在脑海里从第一句往后接。'};}
  if(type==='timed')return {type,poemId:poem.id,prompt:`墨团子只给你一点时间：诗里真的出现了什么？`,answer:poem.imagery[0],options:unique([poem.imagery[0],...distractPoems(poems,poem,'theme'),...poem.imagery.slice(1)]).slice(0,4),tip:`先想《${poem.title}》的第一幅画。`,timed:true};
  if(type==='poet')return {type,poemId:poem.id,prompt:`诗仙信使问：写下《${poem.title}》的人是谁？`,answer:poem.author,options:unique([poem.author,...distractPoems(poems,poem,'author')]),tip:`他生活在${poem.dynasty}。`};
  if(type==='emotion'){const moods={思乡:'想念又安静',童趣:'轻快好奇',孤高:'安静坚定',励志:'开阔向上',惜粮:'认真感恩',边塞:'辽阔豪迈',山水:'惊喜赞叹',自然:'清新自在'};const answer=moods[poem.theme]||'安静欣赏';return {type,poemId:poem.id,prompt:`读《${poem.title}》时，哪种心情最合适？`,answer,options:[answer,'非常生气','急急忙忙','害怕躲藏'],tip:'先想画面的颜色、声音和动作。'};}
  if(type==='identity'){const answer=`《${poem.title}》 · ${poem.author}`;return {type,poemId:poem.id,prompt:'看画面，选出正确的诗名和作者',answer,options:unique([answer,...rotate(poems,poems.indexOf(poem)+1).slice(0,3).map(p=>`《${p.title}》 · ${p.author}`)]),tip:`画里有“${poem.imagery.slice(0,2).join('、')}”。`};}
  return {type:'theme',poemId:poem.id,prompt:`《${poem.title}》主要写的是哪类画面或心情？`,answer:poem.theme,options:unique([poem.theme,...distractPoems(poems,poem,'theme')]),tip:'先说说诗里发生了什么。'};
}

export function createGameRound(mode,poems,count=8,seed=0){
  const allTypes=gameModes.slice(1).map(x=>x.id);
  const types=mode==='mixed'?rotate(allTypes,seed%allTypes.length):Array(count).fill(mode);
  return Array.from({length:count},(_,i)=>createQuestion(types[i%types.length],poems[(seed+i)%poems.length],poems,i));
}

export function pointsForAnswer(correct,attempt=1){return correct?(attempt===1?10:6):0}
export function levelForPoints(points){if(points>=500)return {name:'诗林小先生',icon:'🌳'};if(points>=250)return {name:'花开小诗人',icon:'🌸'};if(points>=100)return {name:'青枝小书童',icon:'🌿'};return {name:'新芽小书童',icon:'🌱'}}
