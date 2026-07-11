const KEY='poem-scholar-v1';
export const defaults={profile:null,settings:{sound:true,music:false,font:'normal',pinyin:true,minutes:10,taskCount:4},progress:{},activities:[],daily:null,rewards:{points:0,gamesCompleted:0,poemsCompleted:0,minutesLearned:0}};
export const storage={load(){try{return {...structuredClone(defaults),...JSON.parse(localStorage.getItem(KEY)||'{}')}}catch{return structuredClone(defaults)}},save(state){localStorage.setItem(KEY,JSON.stringify(state))},clear(){localStorage.removeItem(KEY)}};
