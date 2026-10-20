// Read-only verification; never logs credential material.
import readline from 'node:readline';
const rl=readline.createInterface({input:process.stdin,terminal:false});
if(process.stdin.isTTY)process.stdin.setRawMode(true);
console.log('Ready for private verification JSON on stdin.');
const line=await new Promise(resolve=>rl.once('line',resolve));rl.close();if(process.stdin.isTTY)process.stdin.setRawMode(false);
const {url,token}=JSON.parse(line);
async function get(path){const target=new URL(path,url);if(target.origin!==new URL(url).origin)throw Error('Unexpected origin');const response=await fetch(target,{headers:token?{'OAI-Sites-Authorization':'Bearer '+token}:{},redirect:'manual'});const body=await response.text();let parsed;try{parsed=JSON.parse(body)}catch{};return {status:response.status,body,parsed}}
const results=[];
for(const path of ['/','/hisse/MRVL/','/hakkimizda/','/analysis-audit.json','/api/update-info']){const r=await get(path);results.push({path,status:r.status,contentVerified:path==='/analysis-audit.json'?r.status===404:path==='/api/update-info'?r.parsed?.sourceCount===10:r.body.includes('Arda')})}
const first=await get('/api/daily-bulletin');const second=await get('/api/daily-bulletin');results.push({path:'/api/daily-bulletin',status:first.status,items:first.parsed?.items?.length,updatedAt:first.parsed?.updatedAt,stale:first.parsed?.stale,sources:first.parsed?.sources,persistentReadback:first.parsed?.updatedAt&&first.parsed?.updatedAt===second.parsed?.updatedAt&&second.parsed?.cached});console.log(JSON.stringify(results));
