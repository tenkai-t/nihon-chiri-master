// Register independently of game startup so a broken document/data load cannot prevent worker repair.
if('serviceWorker'in navigator){window.geoBootRegistration=navigator.serviceWorker.register('sw.js',{updateViaCache:'none'});window.geoBootRegistration.catch(()=>{});}
