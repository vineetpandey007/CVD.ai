const fs = require("fs");
function readFile(name) { return fs.readFileSync("/srv/files/" + name); }
