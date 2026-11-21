/* Synthetic IndexedDB facade used ONLY by the unit/DOM harness, not browser production.
   It emulates asynchronous request completion and transactional scheduling; it does NOT
   prove real IndexedDB crash-safety, origin persistence, or native browser transactions. */
(function(g){
 if(!g.crypto?.randomUUID){let counter=1; const gen=()=>{const s=String(counter++).padStart(12,'0');return `12345678-1234-4234-8234-${s}`;};try{Object.defineProperty(g.crypto,'randomUUID',{value:gen,configurable:true})}catch{}}
 const databases=new Map();
 const copy=x=>x===undefined?undefined:JSON.parse(JSON.stringify(x));
 function baseStore(db,name,tx){
   const m=db.rows.get(name);if(!m)throw Error('Unknown store '+name);
   const os={indexNames:{contains:()=>false},createIndex:()=>({}),get(id){return req('get',id)},getAll(){return req('getAll')},put(obj){return req('put',obj)},add(obj){return req('add',obj)},delete(id){return req('delete',id)}};
   function req(op,val){const r={result:undefined,error:null,onsuccess:null,onerror:null};if(tx)tx.pending++;
    setTimeout(()=>{
      try{if(op==='get')r.result=copy(m.get(val));
      else if(op==='getAll')r.result=Array.from(m.values()).map(copy);
      else if(op==='put'||op==='add'){
        if(op==='add'&&m.has(val.id))throw Error('ConstraintError');m.set(val.id,copy(val));r.result=val.id;
      }else if(op==='delete'){m.delete(val)}
      r.onsuccess?.({target:r});
      }catch(e){r.error=e;r.onerror?.({target:r});if(tx){tx.error=e;tx.onabort?.()}}
      finally{if(tx){tx.pending--;tx.schedule()}}
    },0);return r;
   }return os;
 }
 function makeDB(name,version){const db={name,version,rows:new Map(),objectStoreNames:{contains:n=>db.rows.has(n)},createObjectStore(n){db.rows.set(n,new Map());return baseStore(db,n,null)},transaction(names,mode){const tx={error:null,pending:0,complete:false,closed:false,oncomplete:null,onerror:null,onabort:null,
   objectStore(n){if(!names.includes(n))throw Error('Store is not in transaction '+n);return baseStore(db,n,tx)},
   abort(){if(tx.closed)return;tx.closed=true;tx.onabort?.()},
   schedule(){setTimeout(()=>{if(!tx.closed&&tx.pending===0){tx.closed=true;tx.complete=true;tx.oncomplete?.()}},1)}
   };tx.schedule();return tx},close(){}};return db;}
 const facade={open(name,version){const request={result:null,error:null,transaction:null,onupgradeneeded:null,onsuccess:null,onerror:null,onblocked:null};setTimeout(()=>{const existing=databases.get(name),upgrade=!existing||existing.version<version;const db=existing||makeDB(name,version);db.version=version;databases.set(name,db);request.result=db;request.transaction={objectStore:n=>baseStore(db,n,null)};if(upgrade)request.onupgradeneeded?.({target:request});request.onsuccess?.({target:request})},0);return request},__dbs:databases};
 try{Object.defineProperty(g,'indexedDB',{value:facade,configurable:true,writable:true})}catch(e){g.indexedDB=facade}
})(globalThis);
