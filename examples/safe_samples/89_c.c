void find_user(MYSQL_STMT *stmt, char *name) {
  MYSQL_BIND bind[1] = {0};
  mysql_stmt_prepare(stmt, "SELECT * FROM users WHERE name = ?", 36);
  bind[0].buffer = name; mysql_stmt_bind_param(stmt, bind);
}
