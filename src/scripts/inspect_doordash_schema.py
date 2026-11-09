import json
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://job-boards.greenhouse.io/doordashindia/jobs/5856393"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_selector("form", timeout=15000)

    # Extract all question containers and their exact labels, inputs, and options
    data = page.evaluate('''() => {
        const questions = [];
        document.querySelectorAll('.field-wrapper, .select, .field, fieldset').forEach(el => {
            const label = el.querySelector('label, legend')?.innerText?.trim() || '';
            const input = el.querySelector('input, textarea, select');
            const selectContainer = el.querySelector('.select-shell, [class*="-container"]');
            questions.push({
                label,
                id: input ? input.id : null,
                tagName: input ? input.tagName : null,
                type: input ? input.type : null,
                hasSelect: !!selectContainer
            });
        });

        // Also get Remix Context job data if available
        let remixData = null;
        if (window.__remixContext && window.__remixContext.state && window.__remixContext.state.loaderData) {
            const root = window.__remixContext.state.loaderData['routes/jobs.$jobId'] || window.__remixContext.state.loaderData.root;
            remixData = root;
        }

        return { questions, remixQuestions: remixData ? remixData.job?.questions || remixData.jobPost?.questions : null };
    }''')

    print(json.dumps(data, indent=2))
    browser.close()
