void find_user(Database& db, std::string name) {
  auto query = "SELECT * FROM users WHERE name = '" + name + "'";
  db.exec(query);
}
