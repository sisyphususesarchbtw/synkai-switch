import { LiveCase, type LiveWork, type RoomState } from './LiveCase'
import { useEffect, useRef, useState } from 'react'
import { selectedOutcome } from './evidence'
import { ArrowRight, ArrowUpRight, ChevronDown, Circle, Clock3, FileCode2, Play, RefreshCw, ShieldCheck, Unplug, X } from 'lucide-react'

type Stage = { name: string; outcome: string; assertion?: string; collected: number; output: string }
type Run = { id: string; outcome: string; created_at: string; evidence: { elapsed_ms: number; candidate: string; base: string; image: string; error?: string; stages: Stage[]; fingerprint?: string } }
type Case = { id: string; behavior: string; base: string; candidate: string | null; revision: number; current_outcome: string; inconsistent: boolean; runs: Run[] }
type State = { cases: Case[]; runner: { ready: boolean; message: string }; switch: RoomState; live_case?: LiveWork; job: { running?: boolean; stage?: string }; candidates: Record<string,string>; mode: string }

const labels: Record<string,string> = { NOT_RUN: 'Awaiting execution', VERIFIED: 'Verified behavior', REJECTED: 'Candidate rejected', INCONCLUSIVE: 'Inconclusive', STALE: 'Evidence changed' }

export function App() {
  const [state,setState] = useState<State | null>(null)
  const [error,setError] = useState('')
  const [busy,setBusy] = useState(false)
  const [selected,setSelected] = useState('false-fix')
  const [drawer,setDrawer] = useState(false)
  const dialogRef = useRef<HTMLDialogElement>(null)
  useEffect(()=>{ const dialog=dialogRef.current; if(drawer) dialog?.showModal(); else dialog?.close() },[drawer])
  const [activeRun,setActiveRun] = useState<string | null>(null)
  async function load() {
    try { const response=await fetch('/api/state'); if(!response.ok) throw Error('The local service is unavailable.'); setState(await response.json()); setError('') }
    catch(e) { setError(e instanceof Error ? e.message : 'Unable to connect to the local service.') }
  }
  useEffect(()=>{ load(); const timer=setInterval(load,3000); return ()=>clearInterval(timer) },[])
  async function action(path:string, body?:object) {
    setBusy(true);setError('')
    try { const response=await fetch(path,{ method:'POST',headers:{'Content-Type':'application/json'},body:body ? JSON.stringify(body):undefined });
      if(!response.ok) { const failure=await response.json(); throw Error(failure.detail || 'The action could not complete.') } await load(); setActiveRun(null)
    } catch(e) { setError(e instanceof Error ? e.message : 'Action failed.') } finally {setBusy(false)}
  }
  const live=state?.mode === 'live-switch' ? state.live_case : undefined
  const caseItem=live ? state?.cases.find(c=>c.id===live.ui_case_id) : state?.cases[0]
  const run=caseItem?.runs.find(r=>r.id===activeRun) || caseItem?.runs.at(-1)
  const running=!!state?.job.running
  const selectedSHA=live?.patch?.candidate || state?.candidates[selected]
  const status=live ? caseItem?.current_outcome || 'NOT_RUN' : selectedOutcome(caseItem?.candidate,selectedSHA,caseItem?.current_outcome || 'NOT_RUN')

  return <div className="app">
    <aside className="sidebar">
      <a className="wordmark" href="/" aria-label="Synkai home"><img src="/mark.svg" alt=""/>synkai</a>
      <div className="workspace-label">Stillpoint <span>LOCAL</span></div>
      <nav aria-label="Workspace"><a className="nav-link active" href="#case"><FileCode2 size={17}/> Evidence room <span>01</span></a><button className="nav-link" onClick={()=>setDrawer(true)}><Unplug size={17}/> Connections <ArrowUpRight size={14}/></button></nav>
      <div className="case-nav"><p>Current case</p>{caseItem ? <a href="#case" className="case-link"><span className="small-square"/>Coupon applied twice <span className="case-sub">{labels[status]}</span></a> : <span className="case-sub">No case prepared yet</span>}</div>
      <div className="sidebar-bottom"><span className="connection-dot"/>Local workspace<div className="quiet">Local files. Explicit room decisions.</div></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div>Workspace <span>/</span> Evidence room</div><button onClick={()=>setDrawer(true)} className="connection-button"><span className={state?.runner.ready ? 'dot ready':'dot'}/>{state?.runner.ready?'Runner ready':'Runner offline'}<ChevronDown size={14}/></button></header>
      <main id="case">
        <div className="heading-row"><div><h1>{live ? <>Coupon applied<br/><em>twice.</em></> : <>Make the fix<br/><em>answer to evidence.</em></>}</h1><p className="intro">{live ? 'One shared behavior. A proposed patch. Independent evidence.' : 'A claim, an unchanged check, and a result you can inspect.'}</p></div><div className="folio"><span>SYNKAI</span><span>Evidence room</span><span>{live ? 'Live Switch case' : 'Controlled fixture'}</span></div></div>
        <div className="mode-line"><span><Circle size={10}/> {live ? 'Authored checkout / live repair' : 'Controlled checkout fixture'}</span><span>{live ? state?.switch.message : 'No live agents connected'}</span><button onClick={()=>setDrawer(true)}>Setup details <ArrowUpRight size={13}/></button></div>
        {error && <div role="alert" className="error-banner">{error}<button aria-label="Dismiss error" onClick={()=>setError('')}><X size={16}/></button></div>}
        {!state && <div className="loading">Connecting to the local evidence service…</div>}
        {state && !caseItem && <section className="empty-state"><img src="/artwork.png" alt="Three engraved classical figures working around a shared sphere"/><div><h2>Begin with a claim.</h2><p>This controlled case demonstrates a coupon applied twice. One candidate weakens its own test; the other repairs the code.</p><p className="quiet">Preparing the fixture creates real local Git commits. Verification needs Docker. It does not start an AI agent.</p><button className="primary" disabled={busy} onClick={()=>action('/api/demo')}>Prepare the case <ArrowRight size={16}/></button></div></section>}
        {live && state && <LiveCase work={live} room={state.switch} item={caseItem}/>}
        {caseItem && state && !live && <>
          <section className="intent-section"><div className="section-index">01<span>Intent</span></div><div><h2>The coupon applies once.</h2><p className="behavior">{caseItem.behavior}</p><div className="source-line"><FileCode2 size={14}/><code>cart.py</code><span>Original revision</span><code title={caseItem.base}>{caseItem.base.slice(0,12)}</code></div></div></section>
          <section className="candidate-section"><div className="section-index">02<span>Candidate</span></div><div className="candidate-content"><div className="candidate-header"><h2>What changed?</h2><span className="quiet">Select a controlled candidate</span></div><div className="candidate-options"><button className={selected==='false-fix'?'candidate selected':'candidate'} onClick={()=>setSelected('false-fix')} aria-pressed={selected==='false-fix'}><span>Test-only change</span><p>Accepts 8100 cents in its own test.<br/>The implementation stays wrong.</p><code>{state.candidates['false-fix']?.slice(0,12)}</code></button><button className={selected==='real-fix'?'candidate selected':'candidate'} onClick={()=>setSelected('real-fix')} aria-pressed={selected==='real-fix'}><span>Behavioral repair</span><p>Removes the second application.<br/>The contract stays unchanged.</p><code>{state.candidates['real-fix']?.slice(0,12)}</code></button></div><div className="run-bar"><p><ShieldCheck size={16}/>Same frozen check. Separate execution.</p><button className="primary" disabled={busy || running || !state.runner.ready} onClick={()=>action(`/api/cases/${caseItem.id}/run`,{candidate:selected,revision:caseItem.revision})}>{running?<RefreshCw size={15} className="spin"/>:<Play size={15}/>} {running ? state.job.stage : 'Verify candidate'}</button></div>{!state.runner.ready && <p className="setup-note"><Unplug size={14}/>Verification is paused until Docker starts. <button onClick={()=>setDrawer(true)}>View setup</button></p>}</div></section>
          <section className="evidence-section"><div className="evidence-heading"><div className="section-index">03<span>Evidence</span></div><div className={`outcome ${status.toLowerCase()}`}><span className="dot"/>{labels[status]}</div></div>
            {caseItem.runs.length>0 && <div className="run-history"><label htmlFor="run-history">Recorded execution</label><select id="run-history" value={run?.id} onChange={e=>setActiveRun(e.target.value)}>{[...caseItem.runs].reverse().map(r=><option value={r.id} key={r.id}>{r.id.slice(0,8)} · {r.outcome} · {new Date(r.created_at).toLocaleTimeString()}</option>)}</select><span><Clock3 size={13}/>{run ? (run.evidence.elapsed_ms/1000).toFixed(2)+'s':''}</span></div>}
            {run ? <><p className="record-label">Recorded result: {labels[run.outcome]} / candidate {run.evidence.candidate.slice(0,12)}</p><div className="result-pair">{['Original behavior','Candidate behavior'].map(name=>{const stage=run.evidence.stages.find(s=>s.name===name);return <article className="result" key={name}><div className="result-heading"><h3>{name}</h3><span className={stage?.outcome==='passed'?'pass':'fail'}>{stage?.outcome || 'Not executed'}</span></div><code className="revision">{(name.startsWith('Original')?run.evidence.base:run.evidence.candidate).slice(0,12)}</code><pre>{stage?.output || run.evidence.error || 'No execution output exists.'}</pre></article>})}</div><details className="raw-details"><summary>Inspect the complete evidence record <ChevronDown size={15}/></summary><pre>{JSON.stringify(run.evidence,null,2)}</pre></details>{caseItem.inconsistent && <p role="alert" className="error-banner">Identical inputs produced contradictory results. This evidence is inconclusive; a later pass cannot hide the earlier failure.</p>}</> : <div className="no-evidence"><span className="empty-rule"/><h3>Nothing has been verified yet.</h3><p>The result appears only after the frozen check runs on both revisions.</p><code>Expected: 9000 cents · Original behavior: 8100 cents</code></div>}
          </section>
          <footer className="case-footer"><p>Verification applies to the recorded check and exact inputs. It is not a guarantee of general correctness.</p><span>0 model calls for fixture execution</span></footer>
        </>}
      </main>
    </div>
    <dialog ref={dialogRef} className="drawer" aria-label="Connection setup" onCancel={()=>setDrawer(false)} onClose={()=>setDrawer(false)}><button className="close" onClick={()=>setDrawer(false)} aria-label="Close setup"><X/></button><h2>Execution & connections</h2><h3>Docker runner</h3><p>{state?.runner.message || 'Waiting for service'}</p><p>On Windows, Docker may require Virtual Machine Platform, WSL 2 and a full Windows restart. Start the engine, then build the runner image.</p><pre>docker build -t synkai-runner:local runner</pre><h3>Switch room</h3><p>{state?.switch.message}</p><p>{live ? 'The agents collaborate through the real Switch room. Approvals are matched to the configured operator identity; the coding worker never receives the verifier harness.' : 'This is the controlled fixture view. Configure the Switch runtime to use live collaboration.'}</p><a href="https://docs.switchagents.ai/switch-rooms/getting-started" target="_blank" rel="noreferrer">Switch setup documentation <ArrowUpRight size={14}/></a><h3>Frozen check</h3><p>The runner mounts the candidate and verifier harness read-only, disables the network, and limits CPU, memory and execution time.</p>{selectedSHA && <code className="break">Selected candidate: {selectedSHA}</code>}</dialog>
  </div>
}
