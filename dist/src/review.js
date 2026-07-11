export const DAY=86400000;
export function scheduleReview(progress={},result={},now=Date.now()){
  const nodes=[0,2,4,7,14,30]; let level=Math.max(0,Math.min(5,progress.level||0));
  const struggled=!result.correct||(result.hints||0)>2;
  level=struggled?Math.max(1,level-1):Math.min(5,level+1);
  const base=nodes[Math.min(level,nodes.length-1)];
  const interval=struggled?Math.max(1,Math.ceil((progress.intervalDays||base||1)/2)):Math.max(base,progress.intervalDays||0);
  return {...progress,level,intervalDays:interval,nextReviewAt:now+interval*DAY,lastLearnedAt:now,hints:(progress.hints||0)+(result.hints||0),streak:result.correct?(progress.streak||0)+1:0};
}
export function taskPriority(poem,progress={},now=Date.now()){
  if(progress.nextReviewAt&&progress.nextReviewAt<=now)return 400;
  if((progress.errors||[]).length||progress.hints>2)return 300;
  if(poem.grade===2)return 200;
  return progress.level?100:50;
}
export function createDailyTasks(poems,progress={},count=4,now=Date.now()){
  const sorted=[...poems].sort((a,b)=>taskPriority(b,progress[b.id],now)-taskPriority(a,progress[a.id],now));
  const kinds=['到期复习','易错强化','重点巩固','新诗学习','综合挑战'];
  return sorted.slice(0,count).map((poem,i)=>({id:`${new Date(now).toISOString().slice(0,10)}-${poem.id}`,poemId:poem.id,kind:kinds[Math.min(i,kinds.length-1)],done:false}));
}
