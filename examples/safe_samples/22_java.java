String readFile(String name) throws Exception {
  Path root = Path.of("/srv/files").toRealPath();
  Path target = root.resolve(name).normalize();
  if (!target.startsWith(root)) throw new SecurityException();
  return Files.readString(target);
}
