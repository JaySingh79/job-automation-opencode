const fs = require('fs');
const t = fs.readFileSync('src/application_progress/ats_progress.json', 'utf8');
let depth = 0;
let instr = false;
let esc = false;
let rootClose = -1;
for (let i = 0; i < t.length; i++) {
  const c = t[i];
  if (instr) {
    if (esc) { esc = false; } else if (c === '\\') { esc = true; } else if (c === '"') { instr = false; }
    continue;
  }
  if (c === '"') { instr = true; continue; }
  if (c === '{' || c === '[') { depth++; continue; }
  if (c === '}' || c === ']') {
    depth--;
    if (depth === 0 && rootClose === -1) { rootClose = i; }
    continue;
  }
}
console.log('rootClose=' + rootClose + ' len=' + t.length);
console.log('after=' + JSON.stringify(t.slice(rootClose, rootClose + 200)));
const lines = t.split('\n');
console.log('totalLines=' + lines.length);
console.log('around-1645:');
for (let i = 1640; i < 1650 && i < lines.length; i++) { console.log((i + 1) + ': ' + lines[i]); }
