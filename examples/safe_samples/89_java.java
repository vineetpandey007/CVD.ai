void findUser(Connection db, String name) throws Exception {
  PreparedStatement stmt = db.prepareStatement("SELECT * FROM users WHERE name = ?");
  stmt.setString(1, name); stmt.executeQuery();
}
