
const fs = require('fs');
const cp = require('child_process');

async function processJob(page, job, recordJob) {
  const myPage = await page.context().newPage();
  try {
    await myPage.goto(job.url, { timeout: 35000, waitUntil: 'domcontentloaded' });
    await myPage.waitForTimeout(2500);

    // 4 smooth viewport scrolls
    const scrollHeight = await myPage.evaluate(() => document.body.scrollHeight || 3000);
    for (const frac of [0.25, 0.50, 0.75, 1.0]) {
      await myPage.evaluate(h => window.scrollTo({ top: h, behavior: 'smooth' }), scrollHeight * frac);
      await myPage.waitForTimeout(300);
    }
    await myPage.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
    await myPage.waitForTimeout(500);

    // Check error
    const pageText = await myPage.evaluate(() => document.body.innerText);
    if (/error while processing your job application/i.test(pageText)) {
      const res = recordJob('error', 'server_processing_error');
      await myPage.close();
      return { status: 'error', res };
    }

    // Check already applied
    const state = await myPage.evaluate(() => {
      const body = document.body.innerText;
      const already = /already applied|application sent/i.test(body);
      const applyBtn = document.querySelector('#apply-button, .apply-button, button.apply-button');
      const btnText = applyBtn ? applyBtn.innerText.trim() : null;
      const isVisible = applyBtn ? (applyBtn.offsetWidth > 0 || applyBtn.offsetHeight > 0) : false;
      return { already, btnText, hasApplyBtn: !!applyBtn && isVisible };
    });

    if (state.already || (state.btnText || '').toLowerCase() === 'applied') {
      const res = recordJob('already_applied', 'Already applied on page');
      await myPage.close();
      return { status: 'already_applied', res };
    }

    if (!state.hasApplyBtn) {
      const res = recordJob('skipped', 'No native apply button found');
      await myPage.close();
      return { status: 'skipped', res };
    }

    if (/company site/i.test(state.btnText || '')) {
      const res = recordJob('skipped', 'Apply on company site');
      await myPage.close();
      return { status: 'skipped', res };
    }

    // Click Apply via DOM evaluate
    await myPage.evaluate(() => {
      const btn = document.querySelector('#apply-button, .apply-button, button.apply-button');
      if (btn) btn.click();
    });
    await myPage.waitForTimeout(3500);

    // Check confirmation or saveApply
    let currUrl = myPage.url();
    if (/saveApply|confirmation/i.test(currUrl)) {
      const res = recordJob('applied', 'confirmation');
      await myPage.close();
      return { status: 'applied', res };
    }

    // Check chatbot
    let isChat = false;
    try {
      isChat = await myPage.evaluate(() => !!document.querySelector('.chatbot_MessageContainer'));
    } catch (_) {}

    if (isChat) {
      for (let step = 0; step < 15; step++) {
        await myPage.waitForTimeout(1500);
        try {
          currUrl = myPage.url();
          if (/saveApply|confirmation/i.test(currUrl)) break;

          const chatState = await myPage.evaluate(() => {
            const msgs = Array.from(document.querySelectorAll('.chatbot_ListItem, .botMsg')).map(m => m.innerText.trim());
            const text = msgs.slice(-4).join(' ');
            const hasError = /error while processing your job application/i.test(document.body.innerText);
            const hasThankYou = /thank you/i.test(text);
            const hasPAN = /pan/i.test(text);
            const hasGrad = /graduation|grad|batch|year/i.test(text);
            const hasLocation = /location|city|preferred location/i.test(text);
            const hasExp = /experience/i.test(text);
            const hasNotice = /notice/i.test(text);
            const hasCTC = /ctc|salary|lpa/i.test(text);
            const hasTech = /framework|technical|tool|skill|language|python|pytorch|model|rag/i.test(text);
            const hasEditable = !!document.querySelector('.textArea[contenteditable="true"]');
            const hasLabel2026 = !!document.querySelector('label[for="2026"]');
            const hasMcc = !!document.querySelector('.multicheckboxes-container');
            return { text, hasError, hasThankYou, hasPAN, hasGrad, hasLocation, hasExp, hasNotice, hasCTC, hasTech, hasEditable, hasLabel2026, hasMcc };
          });

          if (chatState.hasError) {
            const res = recordJob('error', 'server_processing_error');
            await myPage.close();
            return { status: 'error', res };
          }

          if (chatState.hasThankYou) {
            await myPage.waitForTimeout(2000);
            break;
          }

          if (chatState.hasPAN && chatState.hasEditable) {
            await myPage.evaluate(() => {
              const ed = document.querySelector('.textArea[contenteditable="true"]');
              if (ed) { ed.innerText = 'OVFPS0023B'; ed.dispatchEvent(new Event('input', { bubbles: true })); ed.dispatchEvent(new Event('change', { bubbles: true })); }
            });
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasGrad && chatState.hasLabel2026) {
            await myPage.click('label[for="2026"]');
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasGrad && chatState.hasEditable) {
            await myPage.evaluate(() => {
              const ed = document.querySelector('.textArea[contenteditable="true"]');
              if (ed) { ed.innerText = '2026'; ed.dispatchEvent(new Event('input', { bubbles: true })); ed.dispatchEvent(new Event('change', { bubbles: true })); }
            });
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasLocation && chatState.hasEditable) {
            await myPage.evaluate(() => {
              const ed = document.querySelector('.textArea[contenteditable="true"]');
              if (ed) { ed.innerText = 'Gurgaon'; ed.dispatchEvent(new Event('input', { bubbles: true })); ed.dispatchEvent(new Event('change', { bubbles: true })); }
            });
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasExp && chatState.hasEditable) {
            await myPage.evaluate(() => {
              const ed = document.querySelector('.textArea[contenteditable="true"]');
              if (ed) { ed.innerText = '1.5 Years'; ed.dispatchEvent(new Event('input', { bubbles: true })); ed.dispatchEvent(new Event('change', { bubbles: true })); }
            });
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasNotice && chatState.hasEditable) {
            await myPage.evaluate(() => {
              const ed = document.querySelector('.textArea[contenteditable="true"]');
              if (ed) { ed.innerText = 'Immediate'; ed.dispatchEvent(new Event('input', { bubbles: true })); ed.dispatchEvent(new Event('change', { bubbles: true })); }
            });
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasCTC && chatState.hasEditable) {
            const val = /current/i.test(chatState.text) ? '18 LPA' : '22 LPA';
            await myPage.evaluate(v => {
              const ed = document.querySelector('.textArea[contenteditable="true"]');
              if (ed) { ed.innerText = v; ed.dispatchEvent(new Event('input', { bubbles: true })); ed.dispatchEvent(new Event('change', { bubbles: true })); }
            }, val);
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasTech && chatState.hasEditable) {
            await myPage.evaluate(() => {
              const ed = document.querySelector('.textArea[contenteditable="true"]');
              if (ed) { ed.innerText = 'PyTorch, Hugging Face, LangGraph, RAG'; ed.dispatchEvent(new Event('input', { bubbles: true })); ed.dispatchEvent(new Event('change', { bubbles: true })); }
            });
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasMcc) {
            await myPage.evaluate(() => {
              const inputs = Array.from(document.querySelectorAll('.multicheckboxes-container input'));
              for (const inp of inputs) {
                const lbl = document.querySelector(`label[for="${inp.id}"]`)?.innerText || inp.value || '';
                if (/yes|python|ai|ml|agree|2026/i.test(lbl) || inputs.length === 1) { inp.click(); break; }
              }
              if (inputs.length > 0 && !inputs.some(i => i.checked)) inputs[0].click();
            });
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }

          if (chatState.hasEditable) {
            await myPage.evaluate(() => {
              const ed = document.querySelector('.textArea[contenteditable="true"]');
              if (ed && !ed.innerText.trim()) { ed.innerText = 'Yes'; ed.dispatchEvent(new Event('input', { bubbles: true })); ed.dispatchEvent(new Event('change', { bubbles: true })); }
            });
            await myPage.waitForTimeout(400);
            await myPage.click('.sendMsgbtn_container .sendMsg, [id^="sendMsg__"]');
            continue;
          }
        } catch (_) {}
      }
      await myPage.waitForTimeout(3000);
    }

    // Final confirmation check
    currUrl = myPage.url();
    let finalCheck = { isConfirmed: false, hasError: false, url: currUrl };
    try {
      finalCheck = await myPage.evaluate(() => {
        const body = document.body.innerText;
        const url = window.location.href;
        const isConfirmed = /successfully applied|application sent|thank you for applying|apply confirmation/i.test(body) || /saveApply|confirmation/i.test(url);
        const hasError = /error while processing your job application/i.test(body);
        return { isConfirmed, hasError, url, title: document.title };
      });
    } catch (_) {
      if (/saveApply|confirmation/i.test(currUrl)) {
        finalCheck.isConfirmed = true;
      }
    }

    let res = null;
    if (finalCheck.hasError) {
      res = recordJob('error', 'server_processing_error');
    } else if (finalCheck.isConfirmed) {
      res = recordJob('applied', 'confirmation');
    } else {
      res = recordJob('ready_for_human_submission', 'staged_for_review');
    }

    await myPage.close();
    return { status: finalCheck.isConfirmed ? 'applied' : 'ready_for_human_submission', res, url: finalCheck.url };
  } catch (err) {
    const res = recordJob('error', err.message.slice(0, 150));
    try { await myPage.close(); } catch (_) {}
    return { status: 'error', error: err.message, res };
  }
}

module.exports = { processJob };
