const fs = require('fs');
const t = fs.readFileSync('src/application_progress/ats_progress.json', 'utf8');
let depth = 0;
let instr = false;
let esc = false;
const zeros = [];
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
    if (depth === 0) { zeros.push(i); }
    if (depth < 0) { console.log('NEGATIVE at ' + i + ': ' + JSON.stringify(t.slice(Math.max(0, i - 120), i + 60))); break; }
    continue;
  }
}
console.log('zeroCount=' + zeros.length + ' len=' + t.length);
for (const z of zeros) { console.log('zero@' + z + ' ctx=' + JSON.stringify(t.slice(z, z + 80))); }
