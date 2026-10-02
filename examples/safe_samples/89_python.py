def find_user(db, name):
    query = "SELECT * FROM users WHERE name = ?"
    return db.execute(query, (name,)).fetchall()
