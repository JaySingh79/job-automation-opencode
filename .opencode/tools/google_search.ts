import { tool } from "@opencode-ai/plugin/tool"
import { getJson } from "serpapi"

const MAX_CHARS = 15000

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
    const api_key = process.env.SERPAPI_API_KEY ?? process.env.SERP_API_KEY ?? process.env.SERPAPI_KEY
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
      const json = await getJson({
        engine: "google",
        q: query,
        google_domain,
        hl,
        gl,
        start: page * 10,
        api_key,
      })

      const organic = (json as { organic_results?: { title?: string; link?: string; snippet?: string }[] })
        .organic_results
      if (!organic || organic.length === 0) break

      for (const item of organic) {
        collected.push({
          title: item.title ?? "",
          link: item.link ?? "",
          snippet: item.snippet ?? "",
        })
      }
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
