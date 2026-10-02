const serialize = require("node-serialize");
function load(data) { return serialize.unserialize(data); }
