# Browser Automation & Crawling Notes

## 1. Browser Automation Challenges

| Challenge              | Problem                                       | Example                                                   |
| ---------------------- | --------------------------------------------- | --------------------------------------------------------- |
| Dynamic DOM (SPA)      | HTML is empty until JS executes.              | React `<div id="root"></div>` → Products appear after JS. |
| Element Identification | CSS/XPath selectors change.                   | `#buy-btn` → `#buy-button`.                               |
| Anti-Bot               | Fingerprinting, IP, behavior detection.       | Cloudflare blocks automation.                             |
| CAPTCHA                | Human verification required.                  | reCAPTCHA, hCaptcha.                                      |
| Authentication         | Cookies, OAuth, MFA, JWT.                     | Gmail login.                                              |
| Session Persistence    | Preserve cookies/localStorage.                | Avoid repeated login.                                     |
| Popups                 | Overlays block interaction.                   | Cookie consent.                                           |
| iFrames                | Elements exist in another browsing context.   | Stripe payment form.                                      |
| Shadow DOM             | Components encapsulate DOM.                   | `<payment-widget>`.                                       |
| Infinite Scroll        | Content loads on scroll.                      | Instagram feed.                                           |
| Virtualized Lists      | Only visible rows exist in DOM.               | 100k rows → DOM has ~30.                                  |
| Synchronization        | Page loaded ≠ app ready.                      | Wait for network idle.                                    |
| Navigation             | Click may redirect/open tab/download.         | Invoice download.                                         |
| State Explosion        | Same URL, different state.                    | Logged-in vs guest checkout.                              |
| Semantic Grounding     | Map user goal to UI.                          | "Book cheapest flight."                                   |
| Semantic Ambiguity     | Multiple similar buttons.                     | Continue / Continue as Guest.                             |
| Visual-only UI         | Canvas, charts, maps.                         | TradingView chart.                                        |
| DOM vs Vision          | DOM lacks appearance; vision lacks precision. | Hidden button vs visible button.                          |
| Downloads              | Handle browser↔filesystem.                    | Invoice PDF.                                              |
| File Understanding     | Parse PDF/Excel/Image.                        | OCR invoice.                                              |
| Multi-tab              | OAuth/payment flows.                          | Google Login.                                             |
| Network APIs           | Data fetched via XHR/GraphQL.                 | "Load More".                                              |
| Error Recovery         | Retry intelligently.                          | Detached element.                                         |
| Idempotency            | Avoid duplicate actions.                      | Double payment.                                           |
| Long Horizon           | 20–50 dependent actions.                      | Flight booking.                                           |
| Memory                 | Remember previous state.                      | Selected airline.                                         |
| Context Window         | Huge DOMs.                                    | 150k-token HTML.                                          |
| Prompt Injection       | Malicious webpage instructions.               | "Ignore previous prompt."                                 |
| Credentials            | Protect secrets.                              | Password manager.                                         |
| Permissions            | High-risk actions.                            | Delete repo.                                              |
| Confirmation           | Human approval.                               | Payment.                                                  |
| Observability          | Logs, screenshots, DOM.                       | Debug failures.                                           |
| Reproducibility        | UI changes.                                   | A/B tests.                                                |
| Resources              | Chromium is heavy.                            | RAM/CPU.                                                  |
| Concurrency            | Thousands of sessions.                        | Browser pool.                                             |
| Isolation              | Separate cookies/storage.                     | Multi-user SaaS.                                          |
| Geography              | Region-specific content.                      | US vs India pricing.                                      |
| Cost                   | Browser + LLM latency.                        | 30-step workflow.                                         |
| Website Changes        | UI redesign breaks automation.                | New selectors.                                            |
| Evaluation             | Verify task success.                          | Booking confirmed?                                        |

## 2. Claude vs Firecrawl

| Claude                       | Firecrawl                                            |
| ---------------------------- | ---------------------------------------------------- |
| Search → Reason → Answer     | Search → Crawl → Render JS → Extract → Markdown/JSON |
| Optimized for answer quality | Optimized for machine-readable data                  |
| Research assistant           | Data acquisition platform                            |
| Human-readable output        | LLM/RAG-ready output                                 |
| Not bulk crawling            | Production-scale crawling                            |

## 3. Production Crawling Pipeline

```text
URL Queue → Scheduler → Browser Pool → Render JS → Extract → Clean → Chunk → Metadata → Embeddings → Vector DB
```

## 4. JS Rendering

Without JS:

```html
<div id="root"></div>
```

With JS:

```text
HTML → Execute JS → Render DOM → Extract
```

Interactive elements are one of the biggest challenges because the desired content is often hidden until a user performs an action.

Common issues include:

Interactive                             Element	Challenge	                        Example
Buttons	                                Must be clicked to reveal content	        "Load More", "Show Reviews"
Dropdowns	                            Need selection before data appears	        Choose a country to see shipping costs
Forms	                                Require valid input and submission	        Search box, login form
Infinite Scroll	                        More content loads only while scrolling	    Instagram, LinkedIn feeds
Tabs	                                Content is hidden in inactive tabs	        "Overview", "Reviews", "Specifications"
Accordions	                            Sections remain collapsed until expanded	FAQ pages
Pop-ups/Modals	                        Can block interaction with the page	        Cookie consent, newsletter popup
Date Pickers	                        Require multiple clicks and selections	    Flight booking websites
Pagination	                            Content spans multiple pages	            Google search results
Drag & Drop	                            Requires complex mouse interactions	        Kanban boards like Trello

| Challenge                             | Can modern browser crawlers handle it automatically? |
| ------------------------------------- | :--------------------------------------------------: |
| JavaScript rendering                  |                         ✅ Yes                        |
| Clicking buttons                      |                       ✅ Usually                      |
| Infinite scrolling                    |                       ✅ Usually                      |
| Pagination                            |                         ✅ Yes                        |
| Dropdowns                             |                       ✅ Usually                      |
| Tabs & accordions                     |                         ✅ Yes                        |
| Form filling                          |              ✅ Yes (if inputs are known)             |
| File downloads/uploads                |                         ✅ Yes                        |
| Multi-step workflows                  |                        ✅ Often                       |
| Login (known credentials)             |                         ✅ Yes                        |
| Dynamic waits                         |                         ✅ Yes                        |
| CAPTCHA / human verification          |                    ❌ Not reliably                    |
| MFA / OTP                             |    ❌ Usually requires human or external auth flow    |
| Unknown workflows                     |                      ⚠ Sometimes                     |
| Complex visual reasoning              |               ⚠ Improving, not perfect               |
| Websites actively blocking automation |                   ❌ Not guaranteed                   |


### Why not?

A crawler follows programmed logic. It cannot always infer:

Which button is the correct one when several look similar.
What values to enter into arbitrary forms.
When a site intentionally requires a human (e.g., CAPTCHA or multi-factor authentication).
Whether performing an action is safe, such as submitting an order or making a payment

## 5. Interactive Elements

* Buttons
* Dropdowns
* Tabs
* Accordions
* Infinite Scroll
* Pagination
* Forms
* Date Pickers
* Drag & Drop
* Modals

Modern browser agents can usually automate these, but not reliably CAPTCHAs/MFA.

# Modern browser crawlers/agents can access:

| Data Source             | Purpose                                                          |
| ----------------------- | ---------------------------------------------------------------- |
| **DOM Tree**            | Elements, text, attributes, hierarchy (primary source)           |
| **Accessibility Tree**  | Semantic UI (`button`, `textbox`, `link`), useful for LLM agents |
| **Visual Screenshot**   | Understand layout, charts, canvas, and visually locate elements  |
| **Rendered CSS/Layout** | Visibility, position, size, whether an element is clickable      |
| **JavaScript Runtime**  | Read variables, execute scripts, inspect page state              |
| **Network Traffic**     | Capture XHR/Fetch/GraphQL/API responses directly                 |
| **Browser Storage**     | Cookies, LocalStorage, SessionStorage, IndexedDB                 |
| **Console & Events**    | Detect JS errors, monitor user interactions                      |
| **Browser APIs**        | URL, history, downloads, permissions, clipboard, etc.            |


## 6. Browser Information Sources

| Source             | Information                                      |
| ------------------ | ------------------------------------------------ |
| DOM                | Structure, attributes, text                      |
| CSS/Layout         | Position, visibility, size                       |
| Accessibility Tree | Semantic role (`button`, `textbox`)              |
| JS Runtime         | React/Vue state, event listeners                 |
| Screenshot         | Visual appearance                                |
| Network            | XHR/Fetch/GraphQL                                |
| Browser Storage    | Cookies, LocalStorage, SessionStorage, IndexedDB |
| Console            | Errors, logs                                     |

Example

On a React app:
Browser
├── DOM
├── Accessibility Tree
├── Screenshot
├── Network Requests (GraphQL)
├── Cookies
├── LocalStorage
└── JS Runtime

## 7. Visual Element = Multi-layer Object

```text
Visual Element
├── DOM
├── CSS/Layout
├── Accessibility
├── JavaScript Runtime
├── Visual Rendering
└── Browser State (Storage + Network)
```

Example ("Buy Now"):

* DOM → `<button id="buy">`
* CSS → Visible, blue, clickable
* Accessibility → Role=button, Name="Buy Now"
* JS → `onclick → addToCart()`
* Screenshot → Blue button with cart icon
* Network → `POST /cart/add`

## 8. Date Picker

### Layers

| Layer              | Example                                        |
| ------------------ | ---------------------------------------------- |
| DOM                | `<input type="date">` or custom calendar DOM   |
| CSS                | Popup, selected day, disabled dates            |
| Accessibility      | `textbox`, `dialog`, `grid`, `gridcell`        |
| JS                 | `openCalendar()`, `selectDate()`, `onChange()` |
| Visual             | Calendar popup                                 |
| Network (optional) | Fetch available slots                          |

So, from an ML/browser-agent perspective:
/ A visual element = DOM + Layout/CSS + Accessibility semantics + JavaScript runtime behavior + Visual appearance + Browser/Network state. /

**A date picker is usually not a single object. It's a collection of DOM elements, CSS, JS behavior, and accessibility semantics.**
For a typical date picker:

| Layer                  | Example                                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| **DOM**                | `<input type="date">` **or** `<input>` + calendar popup `<div>` + buttons + table/grid of dates |
| **CSS/Layout**         | Input box, popup calendar, positioning, visibility, disabled/highlighted dates                  |
| **Accessibility**      | `textbox` or `combobox`, `dialog`, `grid`, `gridcell`, `button`, labels like "Choose date"      |
| **JavaScript**         | `focus → openCalendar()`, `click → selectDate()`, `change → updateState()`, keyboard handlers   |
| **Visual**             | Calendar popup with month, arrows, highlighted selected date                                    |
| **Network (optional)** | Sometimes selecting a date triggers an API call to fetch available slots                        |

Common Variations
1. Native HTML Date Picker ✅
<input type="date">
Browser provides the calendar.

2. Custom JavaScript Date Picker ⭐ (Most common)
<input>
↓
React Calendar
↓
Popup
↓
Select Date
Examples:
Airbnb
Booking.com
Material UI DatePicker

3. Dropdown-based
Day ▼
Month ▼
Year ▼

Three separate dropdowns.

4. Calendar Grid
August
1 2 3 4
5 6 7 8

Click a day.

5. Date Range Picker
Start Date
↓
End Date

Common on hotel and flight sites.

6. Date-Time Picker
Date
↓
Time

Select both.

7. Inline Calendar
Calendar is always visible.
No popup.

8. Autocomplete
Today
Tomorrow
Next Monday
LLM/browser agent chooses one.

9. Text Input
12/08/2026

User types directly.
Validation occurs afterward.

10. Framework-specific Widgets
React
Vue
Angular
Material UI
Ant Design

*Each has different DOM structures but similar semantics.*

*The key insight for browser agents*

A browser agent should not assume "date picker" = <input type="date">.
Instead, it should infer the semantic role:

Goal:
Select a date

↓

Possible implementations:

• HTML input
• React widget
• Calendar popup
• Three dropdowns
• Text box
• Date range selector
• Mobile picker

This is why modern browser agents increasingly combine DOM inspection + accessibility tree + visual reasoning. Different implementations look and behave differently at the DOM level, but semantically they all represent the same concept: "choose a date."


### Variants

1. Native HTML (`<input type="date">`)
2. React/Vue/Angular widget
3. Material UI / Ant Design picker
4. Calendar grid
5. Day/Month/Year dropdowns
6. Date range picker
7. Date-time picker
8. Inline calendar
9. Free-text date input
10. Mobile native picker

## Mental Model

```text
Every UI Element =
DOM
+ CSS/Layout
+ Accessibility Semantics
+ JavaScript Runtime
+ Visual Rendering
+ Browser State
```

## 9. Fast one-shot recon loop (form pages)

Speed rule: **grab all layers of the page in a single batched turn, then only DECIDE + FILL.**
No drip-feed of per-field snapshots — that is what made the Oracle run slow.

### On landing, fire these together (one assistant turn, parallel calls):

1. `browser_snapshot` — accessibility tree + `@ref`s (what you *act* on).
2. `browser_evaluate` running `reconFn` from `page_recon.js` — every interactive element fused
   across DOM + accepted-input contract (`required/maxlength/pattern/inputmode/min/max`) + a11y state
   (`checked/pressed/expanded/invalid/disabled`) + CSS visibility + rect, **keyed in page order**,
   plus counts (`required`, `empty_required`, `honeypots`).
3. `browser_take_screenshot { fullPage: true }` — then `node image_slicing.js <shot>.png slices/`
   to cut a tall page into fixed 1400px tiles keyed `-slice-01..NN` with a manifest. Read the slices
   in order; a field's slice = which tile its `rect.y` falls in.
4. (debug only) `read_console_messages`, `read_network_requests`.

That one turn yields DOM + a11y + CSS + accepted-input + visual + console at once.

### Why the screenshot is NOT optional

The DOM lies. On Oracle `minimumPay` reported `type=text`, no `pattern` — but was numeric-only with a
hidden `maxlength=18`, and required siblings (Currency, Pay Frequency) appeared only after it was
filled. `reconFn` catches `maxlength`/`required`; the **sliced screenshot** catches runtime validation
text ("Enter a whole number.") and conditionally-revealed fields. Use both, always, for money/validated
sections.

### Then: DECIDE -> FILL

- Map each `empty_required` field to a value from `user_profile.json` (+ `work_ex_details.md` for prose).
- **Skip anything with `honeypot: true`.**
- Batch every text/url/email field into ONE `browser_fill_form`; click radios/buttons by `@ref`.
- Long prose fields get article-stripped in transit — set them via the base64 + native-setter trick
  (see `ats/google-forms/observation_importance.md`).
- Comboboxes: open -> type the NAME (not a code) -> click the `gridcell`.
- Verify with one `reconFn` re-run (expect `empty_required: 0`) + one screenshot. Stop. Human submits (G1).

### Artifacts

- `page_recon.js` -> `reconFn()` : paste body into `browser_evaluate`.
- `image_slicing.js` : `node image_slicing.js <input.png> [outDir]` -> keyed tiles + manifest.
