// Dependency-independent type bridge used only until @types/react is installed.
// Stage 09 should replace this with the official React type package.
declare module 'react' { const ReactRuntime: any; export default ReactRuntime; }
declare module 'react-dom/client' { export function createRoot(root:Element): {render(node:any):void}; }
