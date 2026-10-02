void findUser(Connection db, String name) throws Exception {
  Statement stmt = db.createStatement();
  stmt.executeQuery("SELECT * FROM users WHERE name = '" + name + "'");
}
