// Adapter shared by the localhost server and its migration regression test.
export function localRequest(req,body){
 const authority=req.headers.host||'localhost:4173',url=new URL(req.url,`http://${authority}`);
 if(!['localhost','127.0.0.1','[::1]','terminal.local'].includes(url.hostname))throw Error('Local preview only');
 return new Request(url,{method:req.method,headers:req.headers,body:['GET','HEAD'].includes(req.method)?undefined:body});
}
