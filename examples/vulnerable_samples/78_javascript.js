const { exec } = require("child_process");
function lookup(host) { exec("nslookup " + host); }
