Object load(InputStream data) throws Exception {
  return new ObjectInputStream(data).readObject();
}
