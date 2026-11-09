const fs = require('fs');
const t = fs.readFileSync('src/application_progress/ats_progress.json', 'utf8');
console.log('LEN=' + t.length);
const re = /^  "[a-z_0-9]+":/gm;
let m;
while ((m = re.exec(t))) {
  console.log(m.index + ': ' + m[0].slice(0, 70));
}
console.log('HEAD=' + JSON.stringify(t.slice(0, 120)));
console.log('TAIL=' + JSON.stringify(t.slice(-120)));
