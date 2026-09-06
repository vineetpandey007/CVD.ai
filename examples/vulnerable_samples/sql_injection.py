def get_user(connection, username):
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return connection.execute(query).fetchall()
