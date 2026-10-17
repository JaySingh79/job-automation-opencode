import { tool } from "@opencode-ai/plugin/tool"
import { getJson } from "serpapi"
import fs from "node:fs"
import path from "node:path"

const MAX_CHARS = 15000

const KEY_NAMES = ["SERPAPI_API_KEY", "SERP_API_KEY", "SERPAPI_KEY"] as const

/** Bun auto-loads .env from cwd only. Tool cwd isn't always the project root,
 *  so fall back to manually parsing the nearest .env (read-only, never writes). */
function loadEnvFallback(): void {
  for (const k of KEY_NAMES) {
    if (process.env[k]) return
  }
  try {
    const g = globalThis as unknown as Record<string, unknown>
    const bun = g["Bun"] as Record<string, unknown> | undefined
    const bunEnv = bun?.["env"] as Record<string, string | undefined> | undefined
    if (bunEnv) {
      for (const k of KEY_NAMES) {
        const v = bunEnv[k]
        if (v && !process.env[k]) process.env[k] = v
      }
      for (const k of KEY_NAMES) {
        if (process.env[k]) return
      }
    }
  } catch {
    // ignore — fall through to .env file scan
  }
  let dir = process.cwd()
  for (let i = 0; i < 6; i++) {
    const p = path.join(dir, ".env")
    if (fs.existsSync(p)) {
      try {
        const text = fs.readFileSync(p, "utf8")
        for (const line of text.split("\n")) {
          const trimmed = line.trim()
          if (!trimmed || trimmed.startsWith("#")) continue
          const m = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/)
          if (!m) continue
          const [, k, raw] = m
          if (!(KEY_NAMES as readonly string[]).includes(k)) continue
          if (process.env[k]) continue
          let v = raw.trim()
          if (
            (v.startsWith('"') && v.endsWith('"') && v.length >= 2) ||
            (v.startsWith("'") && v.endsWith("'") && v.length >= 2)
          ) {
            v = v.slice(1, -1)
          }
          if (v) process.env[k] = v
        }
      } catch {
        // unreadable .env — ignore
      }
      return
    }
    const parent = path.dirname(dir)
    if (parent === dir) return
    dir = parent
  }
}

function resolveApiKey(): string | undefined {
  loadEnvFallback()
  return process.env.SERPAPI_API_KEY ?? process.env.SERP_API_KEY ?? process.env.SERPAPI_KEY
}

export default tool({
  description:
    "Google search via SerpApi (google engine). Paginated (10 results/page). Requires SERPAPI_API_KEY (or SERP_API_KEY alias) in env. Returns up to num_pages*10 deduped {title, link, snippet} results as JSON.",
  args: {
    query: tool.schema
      .string()
      .describe(
        "SerpApi Google query string, e.g. \"(site:boards.greenhouse.io OR site:jobs.lever.co OR site:ashbyhq.com) ('Machine Learning' OR 'AI' OR 'ML')\"",
      ),
    num_pages: tool.schema
      .number()
      .int()
      .min(1)
      .max(5)
      .optional()
      .describe("Pages to fetch (10 results each), 1-5; default 5 => 50 results"),
    gl: tool.schema.string().optional().describe("Geolocation (default 'us')"),
    hl: tool.schema.string().optional().describe("Host language (default 'en')"),
    google_domain: tool.schema.string().optional().describe("Google domain (default 'google.com')"),
  },
  async execute(args) {
    const api_key = resolveApiKey()
    if (!api_key) {
      return "Error: SERPAPI_API_KEY (or SERP_API_KEY) not set in env/.env"
    }

    const query = args.query
    const num_pages = args.num_pages ?? 5
    const gl = args.gl ?? "us"
    const hl = args.hl ?? "en"
    const google_domain = args.google_domain ?? "google.com"

    const collected: { title: string; link: string; snippet: string }[] = []

    for (let page = 0; page < num_pages; page++) {
      let json: unknown
      try {
        json = await getJson({
          engine: "google",
          q: query,
          google_domain,
          hl,
          gl,
          start: page * 10,
          api_key,
        })
      } catch (err) {
        const msg = err instanceof Error ? `${err.constructor.name}: ${err.message}` : String(err)
        // Key/plan problems fail fast; transient page errors stop pagination.
        if (/api[_-]?key|unauthorized|forbidden|402|quota|credit|plan/i.test(msg) && collected.length === 0) {
          return `Error: SerpApi request failed — ${msg}`
        }
        break
      }

      const body = json as {
        error?: string
        organic_results?: { title?: string; link?: string; snippet?: string }[]
      }
      if (body.error) {
        if (collected.length === 0) {
          return `Error: SerpApi returned an error — ${body.error}`
        }
        break
      }

      const organic = body.organic_results
      if (!organic || organic.length === 0) break

      for (const item of organic) {
        collected.push({
          title: item.title ?? "",
          link: item.link ?? "",
          snippet: item.snippet ?? "",
        })
      }
    }

    if (collected.length === 0) {
      return JSON.stringify({ response: [], note: "No organic_results returned for this query." }, null, 2)
    }

    const seen = new Set<string>()
    const deduped = collected.filter((r) => {
      if (!r.link) return true
      if (seen.has(r.link)) return false
      seen.add(r.link)
      return true
    })

    return JSON.stringify({ response: deduped }, null, 2).slice(0, MAX_CHARS)
  },
})
