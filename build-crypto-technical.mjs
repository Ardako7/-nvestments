// Precalculate dated seed indicators at build time. No provider requests.
import fs from 'node:fs/promises';
import vm from 'node:vm';
let raw='';for await(const chunk of process.stdin)raw+=chunk;
const histories=JSON.parse(raw),scope={Date,Math,Map,Number,WeakMap};
vm.createContext(scope);vm.runInContext(await fs.readFile(new URL('../worker/crypto.js',import.meta.url),'utf8')+';globalThis.calculate=cryptoTechnical;',scope);
for(const h of Object.values(histories)){const t=scope.calculate(h.prices);h.seedSeriesIndices=(t.series||[]).map(p=>h.prices.findIndex(x=>x[0]===p[0]&&x[1]===p[1]));delete t.series;h.seedTechnical=t;h.seedTechnicalVersion=1;}
process.stdout.write(JSON.stringify(histories));
