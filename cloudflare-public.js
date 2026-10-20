// Public adapter: Sites identity is not trusted on an independent origin.
import app from '../dist/server/index.js';
export default {async fetch(request,env,ctx){
 const headers=new Headers(request.headers);
 for(const key of [...headers.keys()])if(key.toLowerCase().startsWith('oai-'))headers.delete(key);
 return app.fetch(new Request(request,{headers}),env,ctx);
}};
