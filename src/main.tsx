import ReactRuntime from 'react';
import { createRoot } from 'react-dom/client';
import {App} from './app.js';
// Shared JSX factory uses global React, set here to the installed React runtime.
(globalThis as any).React = ReactRuntime;
const root=document.getElementById('root');
if(!root)throw new Error('Missing React root element');
createRoot(root).render(ReactRuntime.createElement(App));
