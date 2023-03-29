import React from 'react';
import {createRoot} from 'react-dom/client';
import './styles.css';
function App(){return <main><p className="eyebrow">THE KNOWLEDGE DESK</p><h1>Your company,<br/>clearly sourced.</h1><p>Find the right document. Ask a focused question. Follow the evidence.</p></main>}
createRoot(document.getElementById('root')!).render(<App/>);
