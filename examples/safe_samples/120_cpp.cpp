void copy_name(const std::string& user) {
  char buf[16] = {};
  user.copy(buf, sizeof(buf) - 1);
}
