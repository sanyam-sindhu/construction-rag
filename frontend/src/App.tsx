import { Fragment, useEffect, useRef, useState, type ReactNode } from 'react'
import { ask, getJSON, PAGE_DPI, pageImageUrl, pdfUrl, type AskOptions, type DocInfo, type Health, type Source } from './api'

type Turn = {
  id: number
  question: string
  answer: string
  sources: Source[]
  cited: number[]
  status: 'retrieving' | 'answering' | 'done' | 'error'
  error?: string
  retrievalMs?: number
  totalMs?: number
}

const THEMES = [
  { id: 'paper', label: 'Paper' },
  { id: 'blueprint', label: 'Blueprint' },
  { id: 'ledger', label: 'Ledger' },
] as const
type ThemeId = (typeof THEMES)[number]['id']

const SAMPLES = [
  { q: 'What minimum nominal cover is required for severe exposure, and can it be reduced?', doc: 'IS 456' },
  { q: 'What are the limits on longitudinal reinforcement in a column?', doc: 'IS 456' },
  { q: 'Rate for excavating trenches for 80–300 mm pipes in hard rock requiring blasting', doc: 'BSR 2024' },
  { q: 'What is the basic rate of 400 mm DI K-9 pipe to IS 8329?', doc: 'BSR 2024' },
  { q: 'Who chairs the Empowered Committee that clears state PMGSY proposals?', doc: 'PMGSY · EN → HI' },
  { q: 'पीएमजीएसवाई के अंतर्गत त्रि-स्तरीय गुणवत्ता नियंत्रण प्रणाली क्या है?', doc: 'PMGSY · हिंदी' },
]

function initialTheme(): ThemeId {
  try {
    const t = localStorage.getItem('theme')
    if (THEMES.some((x) => x.id === t)) return t as ThemeId
  } catch {
    /* storage unavailable */
  }
  return 'paper'
}

export default function App() {
  const [docs, setDocs] = useState<DocInfo[]>([])
  const [health, setHealth] = useState<Health | null>(null)
  const [turns, setTurns] = useState<Turn[]>([])
  const [input, setInput] = useState('')
  const [docFilter, setDocFilter] = useState<string[]>([])
  const [opts, setOpts] = useState<Omit<AskOptions, 'docs'>>({ k: 6, mode: 'hybrid', model: 'finetuned' })
  const [selected, setSelected] = useState<Source | null>(null)
  const [busy, setBusy] = useState(false)
  const [theme, setTheme] = useState<ThemeId>(initialTheme)
  const results = useRef<HTMLElement>(null)
  const abort = useRef<AbortController | null>(null)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try {
      localStorage.setItem('theme', theme)
    } catch {
      /* storage unavailable */
    }
  }, [theme])

  useEffect(() => {
    getJSON<DocInfo[]>('/api/documents').then(setDocs).catch(() => {})
    getJSON<Health>('/api/health').then(setHealth).catch(() => {})
  }, [])

  const update = (id: number, patch: Partial<Turn> | ((t: Turn) => Partial<Turn>)) =>
    setTurns((ts) => ts.map((t) => (t.id === id ? { ...t, ...(typeof patch === 'function' ? patch(t) : patch) } : t)))

  async function submit(question: string) {
    question = question.trim()
    if (!question || busy) return
    const id = Date.now()
    setTurns((ts) => [...ts, { id, question, answer: '', sources: [], cited: [], status: 'retrieving' }])
    setInput('')
    setBusy(true)
    results.current?.scrollTo({ top: 0, behavior: 'smooth' })
    abort.current = new AbortController()
    try {
      const stream = ask(question, { ...opts, docs: docFilter.length ? docFilter : null }, abort.current.signal)
      for await (const ev of stream) {
        if (ev.type === 'sources') {
          update(id, { sources: ev.sources, status: 'answering', retrievalMs: ev.retrieval_ms })
          if (ev.sources[0]) setSelected(ev.sources[0])
        } else if (ev.type === 'token') update(id, (t) => ({ answer: t.answer + ev.text }))
        else if (ev.type === 'error') update(id, { status: 'error', error: ev.message })
        else if (ev.type === 'done')
          update(id, (t) => ({ cited: ev.cited, totalMs: ev.total_ms, status: t.status === 'error' ? 'error' : 'done' }))
      }
    } catch (e) {
      if ((e as Error).name !== 'AbortError') update(id, { status: 'error', error: String(e) })
      else update(id, { status: 'done' })
    } finally {
      setBusy(false)
    }
  }

  const allIds = docs.map((d) => d.id)
  const activeDocs = docFilter.length ? docFilter : allIds
  const toggleDoc = (id: string) => {
    const next = activeDocs.includes(id) ? activeDocs.filter((d) => d !== id) : [...activeDocs, id]
    if (next.length === 0) return // keep at least one document searchable
    setDocFilter(next.length === allIds.length ? [] : next)
  }

  return (
    <div className="app">
      <header className="masthead">
        <div className="wordmark">
          <span className="title">Construction Reference Desk</span>
          <span className="subtitle">IS 456:2000 · RHB Basic Schedule of Rates 2024 · PMGSY Guidelines (हिंदी)</span>
        </div>
        <div className="theme-switch" role="radiogroup" aria-label="Theme">
          <span className="label">Theme</span>
          {THEMES.map((t) => (
            <button
              key={t.id}
              type="button"
              role="radio"
              aria-checked={theme === t.id}
              className={theme === t.id ? 'on' : ''}
              onClick={() => setTheme(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      <form
        className="searchbar"
        onSubmit={(e) => {
          e.preventDefault()
          submit(input)
        }}
      >
        <div className="query-row">
          <label htmlFor="q" className="label">
            Query
          </label>
          <input
            id="q"
            type="search"
            autoComplete="off"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g. nominal cover for severe exposure · rate of 300 mm DI pipe · पैरा 5.1 आवंटन"
          />
          {busy ? (
            <button type="button" className="btn secondary" onClick={() => abort.current?.abort()}>
              Cancel
            </button>
          ) : (
            <button className="btn" disabled={!input.trim()}>
              Search
            </button>
          )}
        </div>
        <div className="options">
          <div className="opt-group" role="group" aria-label="Documents">
            <span className="opt-label">Documents</span>
            {docs.map((d) => (
              <label key={d.id} className="check" title={d.kind}>
                <input type="checkbox" checked={activeDocs.includes(d.id)} onChange={() => toggleDoc(d.id)} />
                {d.short}
              </label>
            ))}
          </div>
          <label className="opt">
            Retrieval
            <select value={opts.mode} onChange={(e) => setOpts({ ...opts, mode: e.target.value as AskOptions['mode'] })}>
              <option value="hybrid">hybrid</option>
              <option value="dense">semantic</option>
              <option value="bm25">keyword</option>
            </select>
          </label>
          <label className="opt">
            Embedder
            <select value={opts.model} onChange={(e) => setOpts({ ...opts, model: e.target.value as AskOptions['model'] })}>
              <option value="finetuned">domain-tuned</option>
              <option value="base">base</option>
            </select>
          </label>
          <label className="opt">
            Passages
            <select value={opts.k} onChange={(e) => setOpts({ ...opts, k: Number(e.target.value) })}>
              {[4, 6, 8, 10].map((k) => (
                <option key={k}>{k}</option>
              ))}
            </select>
          </label>
        </div>
      </form>

      <main className="layout">
        <section className="results" ref={results}>
          {turns.length === 0 ? (
            <Catalogue docs={docs} onPick={submit} />
          ) : (
            [...turns]
              .reverse()
              .map((t, i) => (
                <Entry key={t.id} no={turns.length - i} turn={t} selected={selected} onSelect={setSelected} />
              ))
          )}
        </section>

        <aside className="reader">
          {selected ? (
            <Reader source={selected} />
          ) : (
            <div className="reader-empty">
              <div className="frame">
                <strong>No source selected</strong>
                <p>Run a query, then select a reference number to open the page with the passage marked.</p>
              </div>
            </div>
          )}
        </aside>
      </main>

      <footer className="statusline">
        {health ? (
          <>
            <span>{health.chunks.toLocaleString()} passages indexed</span>
            <span>retrieval: BM25 + e5-small ({health.embedder.finetuned_available ? 'domain-tuned' : 'base'})</span>
            <span>summaries: {health.llm.model}</span>
          </>
        ) : (
          <span>connecting to index…</span>
        )}
      </footer>
    </div>
  )
}

function Catalogue({ docs, onPick }: { docs: DocInfo[]; onPick: (q: string) => void }) {
  return (
    <div className="catalogue">
      <h2 className="section-title">Indexed documents</h2>
      <table className="doc-table">
        <thead>
          <tr>
            <th>Document</th>
            <th className="hide-sm">Format</th>
            <th className="hide-sm">Language</th>
            <th className="num">Passages</th>
          </tr>
        </thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.id}>
              <td>
                <span className={`doc doc-${d.id}`}>{d.short}</span>
                <div className="small muted">{d.title}</div>
              </td>
              <td className="hide-sm">{d.kind}</td>
              <td className="hide-sm">{d.lang === 'hi' ? 'Hindi' : 'English'}</td>
              <td className="num">{d.chunks.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="section-title">Sample queries</h2>
      <ul className="samples">
        {SAMPLES.map((s) => (
          <li key={s.q}>
            <button type="button" onClick={() => onPick(s.q)}>
              <span className="sample-doc">{s.doc}</span>
              <span className="sample-q">{s.q}</span>
            </button>
          </li>
        ))}
      </ul>
      <p className="note">
        Every result lists the passages it was drawn from, with clause, item or paragraph numbers and page. Selecting a
        reference opens the original page with that passage marked.
      </p>
    </div>
  )
}

function Entry({ no, turn, selected, onSelect }: { no: number; turn: Turn; selected: Source | null; onSelect: (s: Source) => void }) {
  const [showAll, setShowAll] = useState(false)
  const bySrc = new Map(turn.sources.map((s) => [s.n, s]))
  const cited = turn.sources.filter((s) => turn.cited.includes(s.n))
  const listed = showAll || turn.status !== 'done' || cited.length === 0 ? turn.sources : cited

  return (
    <article className="entry">
      <header className="entry-head">
        <span className="entry-no">Q{no}</span>
        <h2 className="entry-q">{turn.question}</h2>
        <span className="entry-meta">
          {turn.retrievalMs != null && `${turn.retrievalMs} ms`}
          {turn.totalMs != null && ` · ${(turn.totalMs / 1000).toFixed(1)} s`}
        </span>
      </header>

      <div className="block">
        <div className="block-label">Summary</div>
        <div className="block-body summary">
          {turn.status === 'retrieving' && <Progress text="Retrieving passages…" />}
          {turn.status === 'answering' && !turn.answer && <Progress text={`Reading ${turn.sources.length} passages…`} />}
          {turn.answer && <Markdown text={turn.answer} sources={bySrc} onCite={onSelect} />}
          {turn.error && <p className="error">Error — {turn.error}</p>}
        </div>
      </div>

      {turn.sources.length > 0 && (
        <div className="block">
          <div className="block-label">Sources</div>
          <div className="block-body">
            <div className="refs-head">
              <span>
                {turn.status === 'done' && cited.length > 0 && !showAll
                  ? `${cited.length} cited of ${turn.sources.length} retrieved`
                  : `${turn.sources.length} retrieved`}
              </span>
              {turn.status === 'done' && cited.length > 0 && cited.length < turn.sources.length && (
                <button type="button" className="link" onClick={() => setShowAll(!showAll)}>
                  {showAll ? 'show cited only' : 'show all retrieved'}
                </button>
              )}
            </div>
            <ol className="refs">
              {listed.map((s) => (
                <RefItem key={s.id} s={s} cited={turn.cited.includes(s.n)} active={selected?.id === s.id} onClick={() => onSelect(s)} />
              ))}
            </ol>
            {turn.status === 'done' && (
              <p className="note">Summary is machine-generated from the passages above. Confirm values on the marked source page.</p>
            )}
          </div>
        </div>
      )}
    </article>
  )
}

function RefItem({ s, cited, active, onClick }: { s: Source; cited: boolean; active: boolean; onClick: () => void }) {
  const [open, setOpen] = useState(false)
  const body = s.text.replace(/^\[[^\]]*\]\n/, '')
  return (
    <li className={`ref ${active ? 'active' : ''} ${cited ? 'cited' : ''}`}>
      <button type="button" className="ref-main" onClick={onClick}>
        <span className="ref-no">{s.n}</span>
        <span className="ref-cite">
          <span className={`doc doc-${s.doc_id}`}>{s.doc}</span> {s.ref}, p. {s.page_label}
        </span>
        <span className="ref-ranks" title="Rank in keyword (BM25) and semantic (dense) search before fusion">
          kw {s.bm25_rank ?? '–'} · sem {s.dense_rank ?? '–'}
        </span>
      </button>
      <p lang={s.lang} className={open ? 'excerpt open' : 'excerpt'}>
        {body}
      </p>
      <button type="button" className="link" onClick={() => setOpen(!open)}>
        {open ? 'collapse' : 'expand'}
      </button>
    </li>
  )
}

function Reader({ source }: { source: Source }) {
  const pages = Object.keys(source.boxes ?? {}).map(Number).sort((a, b) => a - b)
  const [page, setPage] = useState(source.page)
  const scroller = useRef<HTMLDivElement>(null)
  useEffect(() => setPage(source.page), [source.id, source.page])

  // Scroll so the first marked box sits near the top of the panel.
  const onLoad = (img: HTMLImageElement) => {
    const box = source.boxes?.[String(page)]?.[0]
    if (!scroller.current) return
    const scale = (PAGE_DPI / 72) * (img.clientWidth / img.naturalWidth)
    scroller.current.scrollTop = box ? Math.max(0, box[1] * scale - 90) : 0
  }

  return (
    <>
      <div className="reader-head">
        <div className="reader-title">
          <span className="label">Source page</span>
          <strong>
            <span className={`doc doc-${source.doc_id}`}>{source.doc}</span> {source.ref}
          </strong>
          <span className="muted">
            printed p. {source.page_label} · PDF p. {page}
          </span>
        </div>
        <div className="reader-actions">
          {pages.length > 1 &&
            pages.map((p) => (
              <button type="button" key={p} className={`tab ${p === page ? 'on' : ''}`} onClick={() => setPage(p)}>
                p. {p}
              </button>
            ))}
          <a href={pdfUrl({ doc_id: source.doc_id, page })} target="_blank" rel="noreferrer">
            Open PDF
          </a>
        </div>
      </div>
      <div className="page-scroll" ref={scroller}>
        <img
          key={`${source.id}-${page}`}
          src={pageImageUrl(source, page)}
          alt={`${source.doc} page ${page}`}
          onLoad={(e) => onLoad(e.currentTarget)}
        />
      </div>
    </>
  )
}

function Progress({ text }: { text: string }) {
  return (
    <div className="progress">
      <span className="bar" />
      <span>{text}</span>
    </div>
  )
}

/** Minimal markdown: paragraphs, bullet lists, **bold**, and [n] rendered as footnote references. */
function Markdown({ text, sources, onCite }: { text: string; sources: Map<number, Source>; onCite: (s: Source) => void }) {
  const inline = (line: string, key: string): ReactNode[] =>
    line.split(/(\*\*[^*]+\*\*|\[\d{1,2}(?:\s*,\s*\d{1,2})*\])/g).map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) return <strong key={`${key}-${i}`}>{part.slice(2, -2)}</strong>
      const m = part.match(/^\[([\d,\s]+)\]$/)
      if (m)
        return (
          <sup key={`${key}-${i}`} className="cite-sup">
            {m[1].split(',').map((n, j) => {
              const src = sources.get(Number(n.trim()))
              return (
                <Fragment key={n}>
                  {j > 0 && ','}
                  {src ? (
                    <button type="button" className="cite" title={`${src.doc} · ${src.ref} · p. ${src.page_label}`} onClick={() => onCite(src)}>
                      {n.trim()}
                    </button>
                  ) : (
                    <span className="cite dead">{n.trim()}</span>
                  )}
                </Fragment>
              )
            })}
          </sup>
        )
      return part
    })

  const blocks: ReactNode[] = []
  let list: ReactNode[] = []
  const flush = () => {
    if (list.length) blocks.push(<ul key={`ul-${blocks.length}`}>{list}</ul>)
    list = []
  }
  text.split('\n').forEach((raw, i) => {
    const line = raw.trimEnd()
    const bullet = line.match(/^\s*(?:[*-]|\d+\.)\s+(.*)$/)
    if (bullet) list.push(<li key={i}>{inline(bullet[1], `l${i}`)}</li>)
    else {
      flush()
      if (line.trim()) blocks.push(<p key={i}>{inline(line.replace(/^#+\s*/, ''), `p${i}`)}</p>)
    }
  })
  flush()
  return <div className="md">{blocks}</div>
}
