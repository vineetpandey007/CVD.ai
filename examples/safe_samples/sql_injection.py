def get_user(connection, username):
    query = "SELECT * FROM users WHERE name = ?"
    return connection.execute(query, (username,)).fetchall()
