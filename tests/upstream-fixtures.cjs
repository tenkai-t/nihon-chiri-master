// Preserve the original history-based assertions in a fresh GitHub repository.
const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto'),baseline=require('./fixtures/upstream-sha256.json');
exports.assertUnchanged=(file,ref)=>{const expected=baseline[ref+':'+file];assert(expected,'Missing pinned baseline: '+ref+':'+file);assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'..',file))).digest('hex'),expected,file+' changed from pinned upstream commit');};
