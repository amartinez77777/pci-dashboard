/** Global, private-content-only route-leave guard. No private draft text leaves this module. */
const dirtyEditors = new Map<string,boolean>();
export function setEditorDirty(id:string,dirty:boolean):void {if(dirty)dirtyEditors.set(id,true);else dirtyEditors.delete(id)}
export function hasDirtyEditors():boolean{return dirtyEditors.size>0}
export function routeRoot(route:string):string{return route.replace(/^#?\/?/,'').split('/')[0]||'command-center'}
export function needsRouteLeaveConfirmation(from:string,to:string):boolean {
 return from.replace(/^#?\/?/,'')!==to.replace(/^#?\/?/,'')&&hasDirtyEditors();
}
export function canNavigateRoute(from:string,to:string,confirmDiscard:()=>boolean):boolean {
 return !needsRouteLeaveConfirmation(from,to)||confirmDiscard();
}
export function rollbackHash(route:string,loc:Pick<Location,'pathname'|'search'>,hist:Pick<History,'state'|'replaceState'>):void {
 hist.replaceState(hist.state,'',loc.pathname+loc.search+'#/'+route.replace(/^#?\/?/,''));
}
export function useRouteDirtyGuard(id:string,dirty:boolean):void {
 React.useEffect(()=>{setEditorDirty(id,dirty);return()=>setEditorDirty(id,false)},[id,dirty]);
}
/** Installed once at app root; unlike beforeunload, hash changes need an explicit guard. */
export function handleBeforeUnload(event:BeforeUnloadEvent):void {
 if(!hasDirtyEditors())return;
 event.preventDefault();event.returnValue='';
}
