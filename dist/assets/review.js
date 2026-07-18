export const DAY=86400000;
export function localDateKey(now=Date.now()){
  const date=new Date(now),pad=value=>String(value).padStart(2,'0');
  return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}`;
}
export function scheduleReview(progress={},result={},now=Date.now()){
  const nodes=[1,3,7,14,30]; let level=Math.max(0,Math.min(5,progress.level||0));
  const struggled=!result.correct||(result.hints||0)>2;
  level=struggled?Math.max(1,level-1):Math.min(5,level+1);
  const delayed=Boolean(progress.lastLearnedAt&&now-progress.lastLearnedAt>=DAY);
  const delayedSuccesses=(progress.delayedSuccesses||0)+(result.correct&&delayed?1:0);
  if(!result.recitation)level=Math.min(level,3);
  if(result.recitation){level=result.selfRating==='independent'?Math.max(level,4):Math.min(level,3)}
  if(level===5&&delayedSuccesses<2)level=4;
  const priorStage=progress.reviewStage??Math.max(-1,(progress.level||0)-1);
  const reviewStage=struggled?Math.max(0,priorStage-1):Math.min(nodes.length-1,priorStage+1);
  const interval=nodes[reviewStage];
  let errors=result.correct?[...(progress.errors||[])]:[...(progress.errors||[]),result.errorType||'需要巩固'].slice(-5);
  const errorSuccesses={...(progress.errorSuccesses||{})},practiceType=result.practiceType||result.errorType;
  if(result.correct&&practiceType&&errors.includes(practiceType)){errorSuccesses[practiceType]=(errorSuccesses[practiceType]||0)+1;if(errorSuccesses[practiceType]>=2){errors=errors.filter(x=>x!==practiceType);delete errorSuccesses[practiceType]}}
  if(!result.correct&&practiceType)errorSuccesses[practiceType]=0;
  return {...progress,level,reviewStage,intervalDays:interval,nextReviewAt:now+interval*DAY,lastLearnedAt:now,hints:(progress.hints||0)+(result.hints||0),streak:result.correct?(progress.streak||0)+1:0,delayedSuccesses,errors,errorSuccesses,lastEvidence:{date:now,type:result.recitation?'背诵自评':practiceType||'练习',result:result.correct?'完成':'需纠正',selfRating:result.selfRating||null}};
}
export function taskPriority(poem,progress={},now=Date.now()){
  if(progress.nextReviewAt&&progress.nextReviewAt<=now)return 400;
  if((progress.errors||[]).length||progress.hints>2)return 300;
  if(poem.grade===2)return 200;
  return progress.level?100:50;
}
export function recommendedPractice(progress={}){
  const errors=progress.errors||[];
  if(errors.some(x=>x.includes('顺序')||x.includes('衔接')))return '诗句排序';
  if(errors.some(x=>x.includes('错字')||x.includes('关键字')||x.includes('回忆')))return '关键字填空';
  if(errors.some(x=>x.includes('理解')||x.includes('主题')||x.includes('季节')))return '诗意情境题';
  if(errors.some(x=>x.includes('背诵')||x.includes('提示')))return '看图背诵';
  if(progress.intervalDays>=30)return '多首诗混合复习';
  if(progress.intervalDays>=14)return '无提示背诵';
  if(progress.intervalDays>=7)return '填空和背诵';
  if(progress.intervalDays>=3)return '诗句排序';
  return '看图回忆';
}
export function createDailyTasks(poems,progress={},count=3,now=Date.now()){
  const date=localDateKey(now),limit=Math.max(3,count);
  const reviews=poems.filter(p=>p.grade<=2).sort((a,b)=>taskPriority(b,progress[b.id],now)-taskPriority(a,progress[a.id],now)).slice(0,2);
  const preview=poems.filter(p=>p.grade===3&&!(progress[p.id]?.level)).concat(poems.filter(p=>!(progress[p.id]?.level)&&p.grade<3)).find(p=>!reviews.includes(p));
  const tasks=reviews.map((poem,i)=>({id:`${date}-${poem.id}`,poemId:poem.id,mode:'review',kind:i===0?'找回快忘记的诗':'复习一首旧诗',practice:recommendedPractice(progress[poem.id]),done:false}));
  if(preview)tasks.push({id:`${date}-${preview.id}`,poemId:preview.id,mode:'new',kind:'认识一首新诗',practice:'完整诗词冒险',done:false});
  const used=new Set(tasks.map(t=>t.poemId));
  for(const poem of [...poems].sort((a,b)=>taskPriority(b,progress[b.id],now)-taskPriority(a,progress[a.id],now))){if(tasks.length>=limit)break;if(!used.has(poem.id)){used.add(poem.id);tasks.push({id:`${date}-${poem.id}`,poemId:poem.id,mode:progress[poem.id]?.level?'review':'new',kind:progress[poem.id]?.level?'复习一首旧诗':'认识一首新诗',practice:recommendedPractice(progress[poem.id]),done:false})}}
  return tasks.slice(0,limit);
}
