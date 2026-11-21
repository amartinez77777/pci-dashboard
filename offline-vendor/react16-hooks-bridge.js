// Offline-only compatibility bridge for the locally available React 16.0.0 UMD runtime.
// NOT part of the Vite/React 18 production application. NOT a replacement for React hooks.
(function(){
  'use strict';
  var original=window.React;
  var construct=original.createElement;
  var wrapperCache=new WeakMap();
  var active=null;
  function getWrapper(fn){
    var cached=wrapperCache.get(fn);if(cached)return cached;
    class Wrapper extends original.Component {
      constructor(p){super(p);this.hooks=[];this.effects=[];this.index=0;this.pending=[];this.unmounted=false}
      render(){this.index=0;this.pending=[];active=this;let view;try{view=fn(this.props)}finally{active=null}return view}
      componentDidMount(){this.runEffects()}
      componentDidUpdate(){this.runEffects()}
      runEffects(){const list=this.pending.slice();this.pending=[];for(const e of list){if(this.unmounted)break;const old=this.effects[e.index];if(old&&typeof old.cleanup==='function')old.cleanup();const cleanup=e.effect();this.effects[e.index]={deps:e.deps,cleanup};}}
      componentWillUnmount(){this.unmounted=true;for(const e of this.effects){if(e&&typeof e.cleanup==='function')e.cleanup()}}
    }
    wrapperCache.set(fn,Wrapper);return Wrapper;
  }
  function elem(type,props){if(typeof type==='function'&&!type.prototype?.isReactComponent)type=getWrapper(type);return construct.apply(original,[type,props].concat(Array.prototype.slice.call(arguments,2)))}
  function useState(initial){if(!active)throw new Error('useState outside component');var instance=active,i=instance.index++;if(!(i in instance.hooks))instance.hooks[i]=typeof initial==='function'?initial():initial;
    return [instance.hooks[i],function(next){if(instance.unmounted)return;var old=instance.hooks[i],value=typeof next==='function'?next(old):next;if(value!==old){instance.hooks[i]=value;instance.forceUpdate()}}];}
  function useEffect(effect,deps){if(!active)throw new Error('useEffect outside component');var instance=active,i=instance.index++,old=instance.effects[i];if(!old||!deps||!old.deps||deps.some(function(v,j){return v!==old.deps[j]})){instance.pending.push({index:i,effect:effect,deps:deps})}}
  function useMemo(fn,deps){if(!active)throw new Error('useMemo outside component');var instance=active,i=instance.index++,old=instance.hooks[i];if(!old||deps.some(function(v,j){return v!==old.deps[j]})){old={deps:deps,value:fn()};instance.hooks[i]=old}return old.value}
  function useRef(initial){if(!active)throw new Error('useRef outside component');var instance=active,i=instance.index++;if(!(i in instance.hooks))instance.hooks[i]={current:initial};return instance.hooks[i];}
  window.React=Object.assign({},original,{createElement:elem,useState:useState,useEffect:useEffect,useMemo:useMemo,useRef:useRef,Fragment:function(props){return elem('div',{style:{display:'contents'}},props.children)}});
})();
