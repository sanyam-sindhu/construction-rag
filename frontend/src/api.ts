export type Source = {
  n: number
  id: string
  doc_id: string
  doc: string
  ref: string
  section: string
  page: number
  page_label: string
  lang: string
  text: string
  score: number
  bm25_rank: number | null
  dense_rank: number | null
  boxes: Record<string, number[][]> // PDF-point highlight boxes, keyed by page
}

export type DocInfo = { id: string; title: string; short: string; kind: string; lang: string; chunks: number }

export type Health = {
  chunks: number
  llm: { backend: string; model: string }
  embedder: { default: string; finetuned_available: boolean }
}

export type AskOptions = {
  k: number
  docs: string[] | null
  mode: 'hybrid' | 'bm25' | 'dense'
  model: 'finetuned' | 'base'
}

export type AskEvent =
  | { type: 'sources'; sources: Source[]; retrieval_ms: number; llm: Health['llm'] }
  | { type: 'token'; text: string }
  | { type: 'error'; message: string }
  | { type: 'done'; cited: number[]; total_ms: number }

export async function getJSON<T>(path: string): Promise<T> {
  const r = await fetch(path)
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
  return r.json()
}

/** POST /api/ask and yield NDJSON events as they stream in. */
export async function* ask(question: string, opts: AskOptions, signal?: AbortSignal): AsyncGenerator<AskEvent> {
  const r = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ question, ...opts }),
    signal,
  })
  if (!r.ok || !r.body) throw new Error(`${r.status} ${await r.text()}`)
  const reader = r.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    let nl
    while ((nl = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, nl).trim()
      buf = buf.slice(nl + 1)
      if (line) yield JSON.parse(line) as AskEvent
    }
  }
}

export const PAGE_DPI = 110
export const pdfUrl = (s: Pick<Source, 'doc_id' | 'page'>) => `/api/pdf/${s.doc_id}#page=${s.page}`
export const pageImageUrl = (s: Pick<Source, 'doc_id' | 'id'>, page: number) =>
  `/api/page/${s.doc_id}/${page}.png?chunk=${encodeURIComponent(s.id)}&dpi=${PAGE_DPI}`
