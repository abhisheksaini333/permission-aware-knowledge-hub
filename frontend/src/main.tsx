import React,{useEffect,useState,useCallback} from 'react';
import {createRoot} from 'react-dom/client';
import {createPkce,authorizationUrl,validateCallback,exchangeCode} from './auth.mjs';
import {apiRequest} from './http.mjs';
import './styles.css';
import {SearchDesk} from './SearchDesk';
import {AdminDesk} from './AdminDesk';
type Config={issuer:string;client_id:string;dense_available:boolean;answers_available:boolean};
type User={subject:string;tenant:string;groups:string[];roles:string[]};
function App(){
 const [config,setConfig]=useState<Config|null>(null),[access,setAccess]=useState(''),[user,setUser]=useState<User|null>(null),[error,setError]=useState(''),[loading,setLoading]=useState(true);
 const request=useCallback((path:string,init?:RequestInit)=>apiRequest(path,access,init),[access]);
 useEffect(()=>{(async()=>{try{const c=await fetch('/api/config').then(r=>r.json());setConfig(c);const params=Object.fromEntries(new URLSearchParams(location.search));if(params.code||params.error){const saved=sessionStorage.getItem('knowledge.pkce');sessionStorage.removeItem('knowledge.pkce');history.replaceState({},'',location.pathname);const flow=saved?JSON.parse(saved):null;const code=validateCallback(flow,params);const tokens=await exchangeCode(c,flow,code,location.origin+'/');setAccess(tokens.access_token);}}catch(e){setError((e as Error).message);}finally{setLoading(false)}})()},[]);
 useEffect(()=>{if(access)request('/api/me').then(setUser).catch(e=>{setError(e.message);setAccess('')})},[access,request]);
 async function signIn(){if(!config)return;const flow=await createPkce();sessionStorage.setItem('knowledge.pkce',JSON.stringify(flow));location.assign(authorizationUrl(config,flow,location.origin+'/'));}
 return <><header className="topbar"><a className="brand" href="/">KH<span>KNOWLEDGE HUB</span></a>{user?<div className="session"><span>{user.tenant} / {user.roles.join(', ')}</span><button className="text-button" onClick={()=>{setAccess('');setUser(null);}}>Sign out</button></div>:<span className="quiet">A source for every answer.</span>}</header><main><p className="eyebrow">THE KNOWLEDGE DESK</p><h1>Your company,<br/>clearly sourced.</h1><p className="intro">Find the right document. Ask a focused question. Follow the evidence.</p>{error&&<div className="notice error" role="alert">{error}</div>}{loading?<p role="status">Opening your workspace…</p>:!user?<section className="welcome"><p>Sign in to search the documents available to your team.</p><button className="primary" onClick={signIn} disabled={!config}>Sign in with company account <span aria-hidden="true">↗</span></button><p className="quiet">Your organization's access rules follow you here.</p></section>:<section className="workspace"><SearchDesk request={request} denseAvailable={!!config?.dense_available}/>{user.roles.includes("admin")&&<AdminDesk request={request}/>}<h2>Workspace access</h2><p className="quiet">Access groups: {user.groups.join(', ')||'Company documents only'}</p><details><summary>Session details</summary><p>Account ID: <code>{user.subject}</code></p></details></section>}</main><footer>Knowledge Hub <span>Evidence first. Access always.</span></footer></>;
}
createRoot(document.getElementById('root')!).render(<App/>);
