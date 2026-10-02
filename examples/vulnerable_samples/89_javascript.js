function findUser(db, name) {
  const query = "SELECT * FROM users WHERE name = '" + name + "'";
  return db.query(query);
}
