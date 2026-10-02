void lookup(char *host) {
  char cmd[256];
  sprintf(cmd, "nslookup %s", host);
  system(cmd);
}
