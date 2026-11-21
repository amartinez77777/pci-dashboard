/** Local-only queries. No network calls, no duplicate store and no analytics payloads. */
import {listRecords,newRecord,putRecord,deleteRecord} from './storage.js';
import {saveLearningTransaction} from './learning-events.js';
import type {PrivateRecord,StoreName} from './types.js';
import {INTELLIGENCE_STORES,type PersonalSnapshot} from './personal-intelligence-model.js';
export async function loadPersonalSnapshot():Promise<PersonalSnapshot>{
 const all=await Promise.all(INTELLIGENCE_STORES.map(store=>listRecords(store)));
 const result:PersonalSnapshot={};INTELLIGENCE_STORES.forEach((store,i)=>{result[store]=all[i]});return result;
}
export async function loadSuggestionPreference():Promise<{enabled:boolean;record?:PrivateRecord}>{
 const rows=await listRecords('profile_preferences');const record=rows.find(x=>x.data.preference_key==='command_center_suggestions');return {enabled:record?record.data.enabled!==false:true,record};
}
export async function saveSuggestionPreference(enabled:boolean,record?:PrivateRecord):Promise<PrivateRecord>{
 const updated:PrivateRecord=record?{...record,updated_at:new Date().toISOString(),data:{...record.data,enabled}}:newRecord('profile_preferences',{preference_key:'command_center_suggestions',enabled},[]);
 await putRecord(updated);return updated;
}
export interface ReflectionDraft{title:string;text:string;tags:string;sensitive:boolean;consented:boolean}
export async function saveArchiveReflection(d:ReflectionDraft,prior?:PrivateRecord):Promise<PrivateRecord>{
 const title=d.title.trim(),text=d.text.trim();
 if(!title||title.length>160||!text||text.length>5000)throw Error('Enter a title (up to 160 characters) and reflection (up to 5,000 characters).');
 const tags=[...new Set(d.tags.split(',').map(x=>x.trim().toLocaleLowerCase()).filter(Boolean))].slice(0,8);
 if(tags.some(tag=>tag.length>35))throw Error('Tags may contain at most 35 characters.');
 if(prior&&prior.store!=='journal_entries')throw Error('This record must be edited in its original module.');
 if(prior?.sensitive&&!d.sensitive)throw Error('To protect this entry, a sensitive record cannot be changed to nonsensitive in this editor.');
 if(d.sensitive&&!d.consented&&!prior?.consent_id)throw Error('Explicit consent is required for sensitive local writing.');
 const consent=d.sensitive&&!prior?.consent_id?newRecord('consents',{scope:'journal_entries',purpose:'User-approved private reflection storage',explicit:true},[]):undefined;
 const now=new Date().toISOString();const data={...(prior?.data||{}),title,text,tags,entry_kind:'reflection',revision_history:[...(Array.isArray(prior?.data.revision_history)?prior!.data.revision_history.slice(-24):[]),...(prior?[{at:prior.updated_at,title:prior.data.title||'',text:prior.data.text||'',tags:prior.data.tags||[]}]:[])]};
 const updated:PrivateRecord=prior?{...prior,updated_at:now,data,sensitive:d.sensitive,consent_id:prior.consent_id||consent?.id}:newRecord('journal_entries',data,[],d.sensitive,consent?.id);
 await saveLearningTransaction([...(consent?[consent]:[]),updated]);return updated;
}
export async function removeArchiveReflection(id:string):Promise<PrivateRecord>{
 const existing=(await listRecords('journal_entries')).find(x=>x.id===id);if(!existing)throw Error('Note no longer exists');
 await deleteRecord('journal_entries',id);return existing;
}
export async function undoRemoveArchiveReflection(record:PrivateRecord):Promise<void>{if(record.store!=='journal_entries')throw Error('Not an archive note');await putRecord(record)}
