# Playwright MCP High-Speed Automation Guide (`@playwright/mcp`)

## 1. Overview & Architecture
`@playwright/mcp` is Microsoft's official Model Context Protocol server that gives AI agents deterministic, token-efficient browser automation capabilities. Instead of relying on raw pixels, screenshots, or coordinate guesswork, it converts the live DOM into a structured **Accessibility Tree Snapshot** (`browser_snapshot`) where interactive elements receive unique reference IDs (e.g. `ref=f6e129`).

---

## 2. Tool Reference & Execution Rules

| Tool | Key Arguments | Usage & Quirks |
| :--- | :--- | :--- |
| `browser_navigate` | `url: string` | Navigates to target URL; wait for DOM content loaded. |
| `browser_snapshot` | `{}` | Returns YAML accessibility tree with `[ref=...]`, labels, roles, and validation states (`[invalid]`, `[required]`). |
| `browser_type` | `target: string (ref)`, `text: string` | Types text into input using real keystrokes. **Always use this or Playwright fill instead of raw JS `.value =`** because React 18 requires synthetic events (`onChange`/`onInput`) to register field values. |
| `browser_click` | `target: string (ref)`, `element?: string` | Clicks element by its reference ID from the snapshot. |
| `browser_file_upload` | `paths: string[]` | **Modal-Gated**: Can ONLY be invoked when a File Chooser modal is active. Flow: `browser_click(Attach button)` → `[File chooser]` modal activates → `browser_file_upload(paths=[...])`. |
| `browser_evaluate` | `function: string` | Executes custom JavaScript in page context. If setting input values directly in JS, must use React native value setter prototype + events: `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, val); el.dispatchEvent(new Event('input', {bubbles: true}));`. |
| `browser_wait_for` | `time: number` | Pauses for N seconds to allow async XHR/fetch or navigation to finish. |
| `browser_tabs` | `action: "list"|"new"|"select"|"close"` | Manages open tabs. Maintain single-tab discipline (`select` or `close`) to prevent agent contention. |

---

## 3. Fast High-Speed Form Filling Pattern (The 5-Step Loop)

### Step 1: Navigate & Recon
```js
// 1. Navigate to posting
await browser_navigate({ url: job_url });
// 2. Snapshot to get current refs
await browser_snapshot({});
```

### Step 2: Batch Fill Mandatory Fields via Keystrokes
Target inputs using their snapshot `ref` IDs:
```js
// Ensures React/Vue/Angular state registers and [invalid] flags disappear
await browser_type({ target: "ref_first_name", text: "Jay" });
await browser_type({ target: "ref_last_name", text: "Singh" });
await browser_type({ target: "ref_email", text: "jays.iitkgp@gmail.com" });
await browser_type({ target: "ref_phone", text: "+91-8651274328" });
await browser_type({ target: "ref_linkedin", text: "https://linkedin.com/in/jay-singh-ds/" });
```

### Step 3: Handle File Upload Modal
```js
// Click the visible Attach button
await browser_click({ target: "ref_attach_button" });
// Immediately pass the absolute file path to the active file chooser
await browser_file_upload({ 
  paths: ["D:\\Projects\\PRACTICE\\firecrawl_test\\Resumes\\Jay Resume GenAI+DS 5th Aug.pdf"] 
});
```

### Step 4: Submit & Verification
```js
// Click terminal submit
await browser_click({ target: "ref_submit_button" });
// Wait for server response
await browser_wait_for({ time: 3 });
// Snapshot to verify confirmation URL and text
const snap = await browser_snapshot({});
```

### 5. Verification & Anti-Bot Traps (Confirmed Live Findings)
1. **Greenhouse Email OTP / Security Code**:
   - Modern Greenhouse instances trigger an email verification challenge: *"Please enter the security code sent to your email"*.
   - **Fix**: The agent must detect the OTP modal, pause, request the 6-digit code from the user, input it, and confirm submission.
2. **Lever hCaptcha Interactive Visual Challenge**:
   - Lever triggers an interactive hCaptcha challenge (`iframe` containing visual puzzle such as *"Please click on the TWO lines that are shorter"*) before processing the final click on `button "Submit application"`.
   - **Fix**: Must be solved via human interaction or accessibility bypass.
3. **React 18 State Trap**:
   - Plain DOM `.value = ...` does not trigger React synthetic events. Text is visually present, but React's internal validator sees `""` and rejects submission with `[invalid] First Name is required`.
   - **Fix**: Always use `browser_type({ target: ref, text: val })` or the prototype setter `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, val)`.
4. **Guaranteed Submission Criteria**:
   - Greenhouse: Confirmation URL contains `/confirmation` + heading `Thank you for applying.`
   - Lever: Confirmation URL contains `/applied` + text `Thank you for applying`
   - Ashby: Confirmation URL contains `/submitted` + text `Thank you for your application`

---

## 4. Platform-Specific Gotchas

### Greenhouse (`job-boards.greenhouse.io`)
- **React State Trap**: Setting `element.value = ...` via simple JS does not update React internal state. Must use `browser_type` or React prototype setter.
- **Phone Country Combobox**: Shows `+91` pill when selected; phone textbox gets `86512 74328`.
- **Custom Screening Questions**: Many tenants require Education dropdowns (`School*`, `Degree*`, `Discipline*`) and Recent Employer.
- **OTP Challenge**: High-volume or automated attempts trigger an Email Security Code challenge.

### Lever (`jobs.lever.co`)
- **Post-Upload Clear Bug**: Attaching a resume often resets the `Current location` field. Always re-fill location after file upload.
- **URL format**: Target `/apply` directly (`jobs.lever.co/<org>/<id>/apply`).

### Ashby (`jobs.ashbyhq.com`)
- **Location Combobox**: Requires clicking `Start typing...`, typing `India`, and pressing Enter to select.
- **Single Page Scroll**: Both overview and form exist on same page or tab; click `Apply` to reveal form fields.
