void response(char *name) {
  printf("Content-Type: text/html\n\n<p>%s</p>", escape_html(name));
}
