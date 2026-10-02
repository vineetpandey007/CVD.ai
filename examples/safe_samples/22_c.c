void read_file(char *name) {
  char path[PATH_MAX], resolved[PATH_MAX];
  snprintf(path, sizeof path, "/srv/files/%s", name);
  if (realpath(path, resolved) && strncmp(resolved, "/srv/files/", 11) == 0) fopen(resolved, "r");
}
