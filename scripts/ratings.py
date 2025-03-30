import sqlite3

conn = sqlite3.connect("spotify_albums.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id TEXT,
    username TEXT,
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (album_id) REFERENCES albums(album_id)
);
""")

conn.commit()
conn.close()