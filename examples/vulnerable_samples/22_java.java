String readFile(String name) throws Exception {
  return Files.readString(Path.of("/srv/files/" + name));
}
