const fs = require("fs"), path = require("path");
function readFile(name) {
  const root = path.resolve("/srv/files"), target = path.resolve(root, name);
  if (!target.startsWith(root + path.sep)) throw new Error("invalid path");
  return fs.readFileSync(target);
}
