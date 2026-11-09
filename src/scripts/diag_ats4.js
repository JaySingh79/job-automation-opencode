const fs = require('fs');
const t = fs.readFileSync('src/application_progress/ats_progress.json', 'utf8');
console.log('LEN=' + t.length);
// find largest passing prefix via binary search on the error boundary
let lo = 0, hi = t.length;
try { JSON.parse(t); console.log('FULL_PARSE_OK'); process.exit(0); } catch (e) { console.log('full fail: ' + e.message); }
// incrementally parse: find first index where prefix [0,i) parses as complete value followed only by whitespace?
// simpler: locate all top-level value boundaries by trying JSON.parse on growing slices is O(n^2); instead scan with our own tokenizer for string spans and report suspicious lines: control chars inside strings.
let instr = false, esc = false, line = 1, bad = [];
for (let i = 0; i < t.length; i++) {
  const c = t[i];
  if (c === '\n') { line++; continue; }
  if (instr) {
    if (esc) { esc = false; continue; }
    if (c === '\\') { esc = true; continue; }
    if (c === '"') { instr = false; continue; }
    if (c === '\r' || c === '\t') { continue; }
    const code = c.charCodeAt(0);
    if (code < 32) { bad.push('ctrl U+' + code.toString(16) + ' at idx ' + i + ' line ' + line); }
    continue;
  }
  if (c === '"') { instr = true; continue; }
}
console.log('control-char-in-string count=' + bad.length);
for (const b of bad.slice(0, 10)) { console.log(b); }
// show text around reported error pos from last failure (parse again to get pos)
try { JSON.parse(t); } catch (e) {
  const m = /position (\d+)/.exec(e.message);
  if (m) {
    const p = parseInt(m[1], 10);
    console.log('ERRCTX=' + JSON.stringify(t.slice(Math.max(0, p - 200), p + 200)));
  }
}
