void read_file(char *name) {
  char path[256];
  sprintf(path, "/srv/files/%s", name);
  FILE *f = fopen(path, "r");
}
