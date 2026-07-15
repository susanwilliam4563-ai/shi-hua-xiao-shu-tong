export const adventureZones=[
 {id:'spring',name:'春日花谷',mark:'花',desc:'花开、鸟鸣和春风住在这里',poemIds:['hua','chun-xiao','cun-ju','xiao-chi','mei-hua']},
 {id:'village',name:'田园村庄',mark:'田',desc:'莲叶、白鹅、农田和童趣',poemIds:['jiang-nan','yong-e','min-nong-er','xiao-er-chui-diao','fu-de-gu-yuan-cao','zeng-liu-jing-wen']},
 {id:'moon',name:'月夜森林',mark:'月',desc:'跟着月光听见安静的心事',poemIds:['gu-lang-yue-xing','jing-ye-si','ye-su-shan-si','ye-shu-suo-jian','wang-dong-ting']},
 {id:'mountain',name:'山水秘境',mark:'山',desc:'登高、看瀑布，也看湖光山色',poemIds:['shan-xing','wang-lu-shan-pu-bu','yin-hu-shang','deng-guan-que-lou']},
 {id:'frontier',name:'边塞古城',mark:'风',desc:'去辽阔草原和寂静雪江探险',poemIds:['chi-le-ge','jiang-xue','feng']},
 {id:'river',name:'长江诗路',mark:'江',desc:'乘一叶小船走过青山大江',poemIds:['wang-tian-men-shan','jue-ju']}
];

export const characters={
 scholar:{name:'小书童',mark:'童',line:'我们一起把画面变成记忆路线。'},
 baize:{name:'白泽先生',mark:'泽',line:'先听懂画面，诗句就不会散开。'},
 ink:{name:'墨团子',mark:'墨',line:'嘿嘿，我把诗句打乱啦，快送它们回家！'},
 typo:{name:'错字精灵',mark:'错',line:'我藏走了一个字，你能把它找回来吗？'},
 messenger:{name:'诗仙信使',mark:'信',line:'闯关完成！你的诗词收藏送到啦。'}
};

export function learnedCount(progress={}){return Object.values(progress).filter(p=>(p.level||0)>0).length}
export function zoneUnlocked(zoneIndex,progress={}){return zoneIndex<2||learnedCount(progress)>=zoneIndex*2}
export function zoneProgress(zone,progress={}){const learned=zone.poemIds.filter(id=>(progress[id]?.level||0)>0).length;return {learned,total:zone.poemIds.length,complete:learned===zone.poemIds.length}}
export function poemAdventureStatus(poem,progress={},unlocked=true,now=Date.now()){
 if(!unlocked)return {id:'locked',label:'尚未解锁'};
 const p=progress[poem.id]||{};
 if(p.nextReviewAt&&p.nextReviewAt<=now)return {id:'review',label:'需要复习'};
 if((p.level||0)>=4)return {id:'mastered',label:'已学会'};
 if((p.level||0)>0)return {id:'learning',label:'正在学习'};
 return {id:'new',label:poem.grade===3?'三年级预习':'一二年级复习'};
}

export function dueSoon(progress={},now=Date.now()){
 return Object.values(progress).filter(p=>p.nextReviewAt&&p.nextReviewAt<=now+86400000).length;
}

export function rhythmGuide(line){
 const chars=[...line.replace(/[，。！？、；：]/g,'')];
 if(chars.length===5)return `${chars.slice(0,2).join('')} / ${chars.slice(2).join('')}`;
 if(chars.length===7)return `${chars.slice(0,2).join('')} / ${chars.slice(2,4).join('')} / ${chars.slice(4).join('')}`;
 if(chars.length>7){const mid=Math.ceil(chars.length/2);return `${chars.slice(0,mid).join('')} / ${chars.slice(mid).join('')}`}
 return chars.join('');
}

const moodByTheme={思乡:'想念又安静',惜春:'珍惜春光',童趣:'轻快好奇',孤高:'安静坚定',励志:'开阔向上',品格:'坚强清雅',惜粮:'认真感恩',边塞:'辽阔豪迈',生命:'有力量',山水:'惊喜赞叹',自然:'清新自在',想象:'神奇好奇',动物:'活泼可爱',勉励:'温暖坚定'};
export function meaningChallenge(poem,index=0){
 const mood=moodByTheme[poem.theme]||'安静欣赏';
 const variants=[
  {prompt:`如果走进《${poem.title}》的画面，最可能先看到什么？`,answer:poem.imagery[0],options:[poem.imagery[0],poem.imagery.at(-1),'热闹街市']},
  {prompt:`读这首诗时，用哪种心情最合适？`,answer:mood,options:[mood,'非常生气','急急忙忙']},
  {prompt:`《${poem.title}》更像发生在哪个季节？`,answer:poem.season,options:['春','夏','秋','冬']}
 ];
 return variants[index%variants.length];
}

export function rewardForPoem(poem){
 return {poemCard:`《${poem.title}》诗词卡`,stamp:`${poem.dynasty}朝印章`,piece:`${poem.theme}画卷碎片`,messenger:`${poem.author}诗人卡`};
}

export function addPoemReward(state,poem){
 const reward=rewardForPoem(poem);
 state.collections=state.collections||{poemCards:[],poetCards:[],stamps:[],pieces:[],bookmarks:[],badges:[]};
 const add=(key,value)=>{if(!state.collections[key].includes(value))state.collections[key].push(value)};
 add('poemCards',reward.poemCard);add('poetCards',reward.messenger);add('stamps',reward.stamp);add('pieces',reward.piece);
 return reward;
}

export function continueRoute(state){
 if(state.resume?.poemId&&state.resume?.step<8)return `learn/${state.resume.poemId}`;
 if(state.activeGame?.type)return `play/${state.activeGame.type}`;
 return null;
}

export function contextLabel(poem){return poem.grade===3?'趣味预习':'轻松复习'}

export function parentAdvice(poems,progress={}){
 const weak=Object.entries(progress).filter(([,p])=>(p.errors||[]).length||p.hints>2).sort((a,b)=>(b[1].errors?.length||0)-(a[1].errors?.length||0)).slice(0,2);
 if(!weak.length)return '本周保持每天 8—10 分钟即可，先复习旧诗，再认识一首新诗。';
 const names=weak.map(([id])=>`《${poems.find(p=>p.id===id)?.title||''}》`).join('和');
 const errors=[...new Set(weak.flatMap(([,p])=>(p.errors||[]).slice(-2)))];
 return `本周暂时不要加快进度，建议重点复习${names}，练习${errors.join('和')||'画面回忆'}。`;
}
