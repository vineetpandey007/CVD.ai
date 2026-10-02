void lookup(char *host) {
  execl("/usr/bin/nslookup", "nslookup", host, (char *)0);
}
