import requests
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
def get_album_data(album_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    response = requests.get(url, headers=headers).json()

    if "error" in response:
        print(f"Error: {response['error']['message']}")
        return None, None, None, None

    album_name = response["name"].lower()  # Convert album name to lowercase
    album_id_generated = generate_album_id(album_name)
    release_date = response["release_date"]
    release_year = release_date.split("-")[0]  # Extract only the year
    album_image_url = response["images"][0]["url"]  # Get the highest quality image
    album_spotify_link = response["external_urls"]["spotify"]  # Get Spotify link

    return album_id_generated, album_name, release_year, album_image_url, album_spotify_link

# Function to download and save album image in static/images/
def save_album_image(album_id, image_url):
    images_folder = "static/images"
    os.makedirs(images_folder, exist_ok=True)  # Ensure folder exists

    image_path = os.path.join(images_folder, f"{album_id}.jpg")
    img_data = requests.get(image_url).content

    with open(image_path, "wb") as img_file:
        img_file.write(img_data)

    print(f"✅ Album image saved: {image_path}")
    return image_path

# Function to store album data in SQLite database
def save_album_to_db(album_id, album_name, release_year, image_path, spotify_link, db_filename="spotify_albums.db"):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Create albums table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS albums (
            album_id TEXT PRIMARY KEY,
            album_name TEXT,
            release_year TEXT,
            image_path TEXT,
            spotify_link TEXT
        )
    """)

    # Insert album data into the database
    cursor.execute("INSERT OR IGNORE INTO albums (album_id, album_name, release_year, image_path, spotify_link) VALUES (?, ?, ?, ?, ?)", 
                   (album_id, album_name, release_year, image_path, spotify_link))

    conn.commit()
    conn.close()
    print(f"✅ Album data saved to database.")

# Run in a loop
while True:
    album_id_input = input("\nEnter Spotify Album ID (or 'exit' to quit): ").strip()
    if album_id_input.lower() == "exit":
        print("Goodbye! 👋")
        break

    album_id, album_name, release_year, album_image_url, spotify_link = get_album_data(album_id_input)
    if album_id:
        image_path = save_album_image(album_id, album_image_url)
        save_album_to_db(album_id, album_name, release_year, image_path, spotify_link)
