import sqlite3
conn = sqlite3.connect("spotify_albums.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM albums")
print(cursor.fetchall())
conn.close()