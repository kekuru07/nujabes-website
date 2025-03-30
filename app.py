from flask import Flask, render_template, jsonify, request
import sqlite3

# Initialize the Flask app
app = Flask(__name__)

# Path to the SQLite database
DB_PATH = "spotify_albums.db"

# Function to fetch all albums from the database
def get_all_albums():
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Fetch album details: album_id, album_name, release_year, image_path
        cursor.execute("SELECT album_id, album_name, release_year, image_path FROM albums")
        albums = cursor.fetchall()

        # Close the database connection
        conn.close()

        # Return a list of albums as dictionaries
        return [
            {"album_id": str(a[0]), "album_name": a[1], "release_year": a[2], "image_path": a[3]}
            for a in albums
        ]
    except Exception as e:
        # Log any errors and return an empty list if the query fails
        print("Database Error:", e)
        return []

# Function to fetch data for a specific album and its songs
def get_album_data(album_id):
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Fetch album details (name, year, image path, Spotify link)
        cursor.execute("SELECT album_name, release_year, image_path, spotify_link FROM albums WHERE album_id = ?", (album_id,))
        album = cursor.fetchone()

        if not album:
            return None  # Return None if the album is not found

        # Prepare album data
        album_data = {
            "album_id": album_id,
            "album_name": album[0],
            "release_year": album[1],
            "image_path": album[2],
            "spotify_link": album[3]
        }

        # Fetch all songs for this album
        cursor.execute("SELECT title, artists, duration, spotify_link FROM songs WHERE album_id = ?", (album_id,))
        songs = cursor.fetchall()

        # Map song data to dictionaries
        song_list = [
            {"title": s[0], "artists": s[1], "duration": s[2], "spotify_link": s[3]}
            for s in songs
        ]

        # Close the database connection
        conn.close()

        # Return album data along with its songs
        return {"album": album_data, "songs": song_list}
    except Exception as e:
        # Log any errors and return None if the query fails
        print("Database Error:", e)
        return None

# Routes

# Home route - Render the homepage
@app.route("/")
def home():
    return render_template("index.html")

# Discography route - Display all albums
@app.route("/discography")
def discography():
    albums = get_all_albums()  # Fetch all albums from the database
    return render_template("discography.html", albums=albums)

# Album page route - Display a specific album's data and its songs
@app.route("/album/<album_id>")
def album_page(album_id):
    album_data = get_album_data(album_id)  # Fetch album data using the album ID
    if not album_data:
        return "Album not found", 404  # Return error if album is not found

    # Fetch reviews for this album
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, rating, comment, created_at FROM reviews WHERE album_id = ? ORDER BY created_at DESC", (album_id,))
    reviews = cursor.fetchall()
    conn.close()

    # Map reviews to dictionaries
    reviews_list = [{"username": r[0], "rating": r[1], "comment": r[2], "created_at": r[3]} for r in reviews]

    # Render the album page template with album data and reviews
    return render_template("album_page.html", album=album_data["album"], songs=album_data["songs"], reviews=reviews_list)

# API route to get all albums in JSON format (for JavaScript)
@app.route("/api/albums", methods=["GET"])
def api_albums():
    return jsonify(get_all_albums())

# API route to get a specific album's data in JSON format
@app.route("/api/album/<album_id>", methods=["GET"])  # Allow string album_id
def api_album(album_id):
    data = get_album_data(album_id)
    return jsonify(data) if data else jsonify({"error": "Album not found"}), 404

# API route to get albums sorted by a specified order (e.g., by name or release year)
@app.route("/api/albums/<sort_order>")
def api_albums_sorted(sort_order):
    sort_options = {
        "year": "release_year DESC",  # Newest albums first
        "nameAsc": "album_name ASC",  # Alphabetical order (ascending)
        "nameDesc": "album_name DESC"  # Alphabetical order (descending)
    }

    # Default to sorting by release year if the sort order is not valid
    order_by = sort_options.get(sort_order, "release_year DESC")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT album_id, album_name, release_year, image_path FROM albums ORDER BY {order_by}")
        albums = cursor.fetchall()
        conn.close()

        # Return albums in JSON format
        return jsonify([
            {"album_id": str(a[0]), "album_name": a[1], "release_year": a[2], "image_path": a[3]}
            for a in albums
        ])
    except Exception as e:
        print("Database Error:", e)
        return jsonify({"error": "Database error"}), 500

# API route to get songs for an album, sorted by a specified order
@app.route("/api/songs/<album_id>/<sort_order>")
def api_songs_sorted(album_id, sort_order):
    sort_options = {
        "titleAsc": "title ASC",     # Sort by title (ascending)
        "titleDesc": "title DESC",   # Sort by title (descending)
        "artistAsc": "artists ASC",  # Sort by artist (ascending)
        "artistDesc": "artists DESC" # Sort by artist (descending)
    }

    # Default to sorting by track number if no valid sort order is provided
    order_by = sort_options.get(sort_order, "track_number ASC")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT title, artists, duration, spotify_link FROM songs WHERE album_id = ? ORDER BY {order_by}", (album_id,))
        songs = cursor.fetchall()
        conn.close()

        # Return songs in JSON format
        return jsonify([
            {"title": s[0], "artists": s[1], "duration": s[2], "spotify_link": s[3]}
            for s in songs
        ])
    except Exception as e:
        print("Database Error:", e)
        return jsonify({"error": "Database error"}), 500

# API routes to fetch albums sorted by different criteria

@app.route("/api/albums/sorted-year")
def get_albums_sorted_by_year():
    return get_sorted_albums("release_year DESC")

@app.route("/api/albums/sorted-nameAsc")
def get_albums_sorted_by_name_asc():
    return get_sorted_albums("album_name ASC")

@app.route("/api/albums/sorted-nameDesc")
def get_albums_sorted_by_name_desc():
    return get_sorted_albums("album_name DESC")

@app.route("/api/albums/sorted-rating")
def get_albums_sorted_by_rating():
    return get_sorted_albums("avg_rating DESC")

# Helper function to retrieve sorted albums
def get_sorted_albums(order_by):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT album.album_id, album.album_name, album.image_path, album.release_year, 
                   COALESCE(AVG(review.rating), 0) AS avg_rating
            FROM albums album
            LEFT JOIN reviews review ON album.album_id = review.album_id
            GROUP BY album.album_id
            ORDER BY {order_by}
        """)
        albums = cursor.fetchall()
        conn.close()

        # Return albums in JSON format
        return jsonify([
            {"id": a[0], "album_name": a[1], "image_path": a[2], "release_year": a[3], "avg_rating": a[4]}
            for a in albums
        ])
    except Exception as e:
        print("Database Error:", e)
        return jsonify({"error": "Database error"}), 500

# API route to get reviews for a specific album
@app.route("/api/reviews/<album_id>")
def get_reviews(album_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Fetch reviews for the given album
        cursor.execute("SELECT username, rating, comment, created_at FROM reviews WHERE album_id = ? ORDER BY created_at DESC", (album_id,))
        reviews = cursor.fetchall()
        conn.close()

        # Map reviews to dictionaries
        reviews_list = [{"username": r[0], "rating": r[1], "comment": r[2], "created_at": r[3]} for r in reviews]
        return jsonify(reviews_list)
    except Exception as e:
        print("Database Error:", e)
        return jsonify({"error": "Database error"}), 500

# API route to submit a review for an album
@app.route("/api/reviews", methods=["POST"])
def submit_review():
    try:
        data = request.json
        album_id = data.get("album_id")
        username = data.get("username")
        rating = int(data.get("rating"))
        comment = data.get("comment")

        # Validate rating input
        if not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        # Insert the review into the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (album_id, username, rating, comment) VALUES (?, ?, ?, ?)", (album_id, username, rating, comment))
        conn.commit()
        conn.close()

        return jsonify({"message": "Review submitted successfully!"})
    except Exception as e:
        print("Database Error:", e)
        return jsonify({"error": "Error submitting review"}), 500

@app.route('/accessibility')
def accessibility():
    return render_template('accessibility.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
