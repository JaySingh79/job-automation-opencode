import { tool } from "@opencode-ai/plugin"
import path from "path"
import fs from "node:fs"

const MAX_CHARS = 6000
const STOPWORDS = new Set(
  "a an the and or of for to in on at with how what when where which who whom whose is are was were be been do does did should would could can it its this that these those from by as into vs via per show list give find get all any our their his her my your tell about".split(
    " ",
  ),
)

function keywords(question: string, limit = 8): string[] {
  const out: string[] = []
  for (const t of question.toLowerCase().match(/[a-z0-9][a-z0-9_\-.]*|[\u0900-\u097F]+/g) ?? []) {
    if (t.length < 3 || STOPWORDS.has(t) || out.includes(t)) continue
    out.push(t)
    if (out.length >= limit) break
  }
  return out
}

function walkMd(dir: string, out: string[] = []): string[] {
  let entries: fs.Dirent[] = []
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true })
  } catch {
    return out
  }
  for (const e of entries) {
    if (e.name.startsWith(".") || e.name === "node_modules") continue
    const full = path.join(dir, e.name)
    if (e.isDirectory()) walkMd(full, out)
    else if (e.isFile() && /\.mdx?$/.test(e.name)) out.push(full)
  }
  return out
}

/** Local-markdown fallback when Neo4j is empty/unreachable. Scores lines by keyword hits. */
function fallbackSearch(root: string, question: string, topK: number): string {
  const atsDir = path.join(root, "ats")
  if (!fs.existsSync(atsDir)) return "Fallback: no ./ats directory found. Nothing to search."
  const keys = keywords(question)
  if (keys.length === 0) return "Fallback: no searchable keywords in query."
  type Hit = { file: string; line: number; text: string; score: number }
  const hits: Hit[] = []
  const files = walkMd(atsDir).slice(0, 200)
  for (const file of files) {
    let stat: fs.Stats
    try {
      stat = fs.statSync(file)
    } catch {
      continue
    }
    if (stat.size > 200_000) continue
    let content: string
    try {
      content = fs.readFileSync(file, "utf8")
    } catch {
      continue
    }
    const lines = content.split("\n")
    for (let i = 0; i < lines.length; i++) {
      const lower = lines[i].toLowerCase()
      let score = 0
      for (const k of keys) if (lower.includes(k)) score++
      if (score > 0) {
        hits.push({
          file: path.relative(root, file).replace(/\\/g, "/"),
          line: i + 1,
          text: lines[i].trim().slice(0, 220),
          score,
        })
      }
    }
  }
  hits.sort((a, b) => b.score - a.score || a.file.localeCompare(b.file))
  const top = hits.slice(0, topK * 3)
  if (top.length === 0)
    return `Fallback (markdown scan of ./ats, keywords: ${keys.join(", ")}): no matches. The graph may need ingest: \`uv run python markdown_to_neo4j_gemini.py\` equivalent cocoindex update over ./ats.`
  const body = top.map((h) => `- ${h.file}:${h.line} — ${h.text}`).join("\n")
  return (
    `Fallback (Neo4j empty/unreachable; markdown scan of ./ats, keywords: ${keys.join(", ")}):\n` +
    body +
    `\n\nNote: populate the graph by running the cocoindex ingest over ./ats, then re-query for relationship context.`
  )
}

function formatGraph(data: {
  keywords: string[]
  entities: string[]
  triples: { subject: string; predicate: string; object: string }[]
  documents: { filename: string; title?: string; summary?: string }[]
}): string {
  const parts: string[] = []
  if (data.entities.length > 0) parts.push(`Matched entities: ${data.entities.join("; ")}`)
  if (data.triples.length > 0) {
    parts.push(
      "Relationships:\n" +
        data.triples.map((t) => `- ${t.subject} --[${t.predicate}]--> ${t.object}`).join("\n"),
    )
  }
  if (data.documents.length > 0) {
    parts.push(
      "Sources:\n" +
        data.documents
          .map((d) => `- ${d.filename}${d.title ? ` — ${d.title}` : ""}${d.summary ? `\n  ${d.summary.slice(0, 300)}` : ""}`)
          .join("\n"),
    )
  }
  return parts.join("\n\n")
}

export default tool({
  description:
    "Fetch grounded context from the repo knowledge graph (Neo4j GraphRAG built from ./ats ATS notes). Use BEFORE filling a job application or answering ATS/process questions: query for the ATS product or topic (e.g. 'Workday searchable prompt gotchas', 'Phenom country field re-render') and cite the returned file anchors. Falls back to a local markdown scan when the graph is empty.",
  args: {
    query: tool.schema.string().describe("Natural-language question, e.g. 'Workday promptSearchButton flow'"),
    top_k: tool.schema
      .number()
      .int()
      .min(1)
      .max(20)
      .optional()
      .describe("Max entities/documents per hop (default 5)"),
  },
  async execute(args, context) {
    const topK = args.top_k ?? 5
    const root = (context as { worktree?: string; directory?: string }).worktree
      ?? (context as { directory?: string }).directory
      ?? process.cwd()
    const script = path.join(root, ".opencode", "tools", "graphrag_query.py")

    try {
      const raw = await Bun.$`uv run python ${script} ${args.query} ${String(topK)}`.cwd(root).text()
      const start = raw.indexOf("{")
      if (start >= 0) {
        const data = JSON.parse(raw.slice(start))
        if (data.mode === "graph") {
          const noHits =
            (data.entities?.length ?? 0) === 0 &&
            (data.triples?.length ?? 0) === 0 &&
            (data.documents?.length ?? 0) === 0
          if (!noHits) return formatGraph(data).slice(0, MAX_CHARS)
          return fallbackSearch(root, args.query, topK).slice(0, MAX_CHARS)
        }
      }
    } catch {
      // Neo4j down, uv missing, parse error — fall through to markdown scan.
    }
    return fallbackSearch(root, args.query, topK).slice(0, MAX_CHARS)
  },
})
