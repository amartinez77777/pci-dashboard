// Minimal browser JSX declaration for the bundled/offline UMD React runtime.
// This is not a substitute for modern React type packages in a future dependency upgrade.
declare const React:{
 createElement(type:any,props?:any,...children:any[]):any;
 useState<T>(initial:T|(()=>T)):[T,(value:T|((previous:T)=>T))=>void];
 useEffect(effect:()=>void|(()=>void),dependencies?:ReadonlyArray<unknown>):void;
 useMemo<T>(compute:()=>T,dependencies:ReadonlyArray<unknown>):T;
 useRef<T>(initial:T):{current:T};
 Fragment:any;
};
declare const ReactDOM:{render(element:any,container:Element):void};
declare namespace JSX{interface IntrinsicElements{[elementName:string]:any}}
