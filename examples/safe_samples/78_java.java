void lookup(String host) throws Exception {
  new ProcessBuilder("nslookup", host).start();
}
