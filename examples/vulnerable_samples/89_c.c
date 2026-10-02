void find_user(MYSQL *db, char *name) {
  char query[256];
  sprintf(query, "SELECT * FROM users WHERE name = '%s'", name);
  mysql_query(db, query);
}
