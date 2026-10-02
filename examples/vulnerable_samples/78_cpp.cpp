void lookup(std::string host) {
  std::string cmd = "nslookup " + host;
  std::system(cmd.c_str());
}
