void find_user(Database& db, std::string name) {
  db.exec("SELECT * FROM users WHERE name = ?", name);
}
