import fs from 'fs';
const code = fs.readFileSync('dist/assets/index-D7J_XCUv.js', 'utf8');
let depth = 0;
let inStr = false;
let inTick = false;
for (let i = 0; i < code.length; i++) {
  const c = code[i];
  const p = i > 0 ? code[i-1] : '';
  if (c === '"' && p !== '\\' && !inTick) inStr = !inStr;
  if (c === '`' && p !== '\\' && !inStr) inTick = !inTick;
  if (!inStr && !inTick) {
    if (c === '{') depth++;
    if (c === '}') depth--;
  }
}
console.log('Original dist brace depth:', depth);
console.log('Length:', code.length);
