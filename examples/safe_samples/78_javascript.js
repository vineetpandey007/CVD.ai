const { execFile } = require("child_process");
function lookup(host) { execFile("nslookup", [host]); }
