import requests
import csv
import os
import sqlite3

# Your Spotify API credentials
CLIENT_ID = "24a9819f55b84d0face315d574bedb40"
CLIENT_SECRET = "fcb291864c994a02a82f13b703f527b4"

# Get access token
AUTH_URL = "https://accounts.spotify.com/api/token"
auth_response = requests.post(AUTH_URL, {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
})

auth_response_data = auth_response.json()
access_token = auth_response_data["access_token"]

# Generate a unique Album ID from the first letters of each word in the album name
def generate_album_id(album_name):
    return "".join(word[0] for word in album_name.split()).lower()

# Function to fetch album data from Spotify API
def get_album_tracks(album_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    response = requests.get(url, headers=headers).json()

    if "error" in response:
        print(f"Error: {response['error']['message']}")
        return None, None, None

    album_name = response["name"].lower()  # Convert album name to lowercase
    album_id_generated = generate_album_id(album_name)
    release_date = response["release_date"]  # Get full release date (YYYY-MM-DD or YYYY)
    release_year = release_date.split("-")[0]  # Extract only the year

    tracks = response["tracks"]["items"]

    data = []
    for track in tracks:
        title = track["name"].lower()
        artists = ", ".join([artist["name"].lower() for artist in track["artists"]])
        duration = track["duration_ms"] // 1000  # Convert to seconds
        spotify_link = track["external_urls"]["spotify"].lower()

        data.append([album_id_generated, title, artists, release_year, f"{duration // 60}:{duration % 60:02d}", spotify_link])

    return album_name, album_id_generated, data

# Function to save album data to CSV
def save_to_csv(album_name, album_id, track_data):
    filename = f"{album_name.replace('/', '-')}.csv"
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["album_id", "title", "artists", "release_year", "duration", "spotify_link"])
        writer.writerows(track_data)

    print(f"✅ Exported: {filename}")
    return filename

# Function to import CSV data into an SQLite database
def import_to_sqlite(csv_filename, db_filename="spotify_albums.db"):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            album_id TEXT,
            title TEXT,
            artists TEXT,
            release_year TEXT,
            duration TEXT,
            spotify_link TEXT
        )
    """)

    # Read CSV and insert data
    with open(csv_filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        cursor.executemany("INSERT INTO songs (album_id, title, artists, release_year, duration, spotify_link) VALUES (?, ?, ?, ?, ?, ?)", reader)

    conn.commit()
    conn.close()
    print(f"✅ Imported {csv_filename} into {db_filename}")

# Run in a loop
while True:
    album_id_input = input("\nEnter Spotify Album ID (or 'exit' to quit): ").strip()
    if album_id_input.lower() == "exit":
        print("Goodbye! 👋")
        break

    album_name, album_id, track_data = get_album_tracks(album_id_input)
    if album_name and track_data:
        csv_filename = save_to_csv(album_name, album_id, track_data)
        import_to_sqlite(csv_filename)
