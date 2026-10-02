void lookup(String host) throws Exception {
  Runtime.getRuntime().exec("nslookup " + host);
}
