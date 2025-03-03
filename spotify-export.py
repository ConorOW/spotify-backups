import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import csv

# Spotify API credentials (Replace with your details)
CLIENT_ID = "42466d43e9ed41ebb90de817918c6bf7"
CLIENT_SECRET = "bd47e3b057494f6db5b534bedb1c4737"
REDIRECT_URI = "http://localhost:8888/callback"

# Set up authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private user-library-read"
))

### Function to extract playlist tracks ###
def get_playlist_tracks(playlist_id, playlist_name):
    tracks = []
    results = sp.playlist_tracks(playlist_id)

    while results:
        for item in results['items']:
            track = item.get('track')  # Avoid KeyError if track is missing
            if track and track.get('name'):
                tracks.append({
                    'Type': 'Playlist',
                    'Playlist': playlist_name,
                    'Artist': ', '.join([artist['name'] for artist in track.get('artists', [])]),
                    'Album': track.get('album', {}).get('name', ''),
                    'Title': track.get('name', ''),
                    'Track ID': track.get('id', ''),
                    'Track URL': track.get('external_urls', {}).get('spotify', '')
                })
            else:
                print(f"Warning: Skipping track due to missing data in {playlist_name}")

        results = sp.next(results) if results else None  # Handle pagination

    return tracks

### Function to extract saved albums ###
def get_saved_albums():
    albums = []
    results = sp.current_user_saved_albums()

    while results:
        for item in results['items']:
            album = item.get('album')
            if album:
                albums.append({
                    'Type': 'Saved Album',
                    'Playlist': '',
                    'Artist': ', '.join([artist['name'] for artist in album.get('artists', [])]),
                    'Album': album.get('name', ''),
                    'Title': '',  # No specific track title for albums
                    'Track ID': album.get('id', ''),
                    'Track URL': album.get('external_urls', {}).get('spotify', '')
                })
        results = sp.next(results) if results else None  # Handle pagination

    return albums

### Main execution ###
all_tracks = []

# Extract all playlists
playlists = sp.current_user_playlists()
for playlist in playlists['items']:
    playlist_name = playlist['name']
    playlist_id = playlist['id']
    print(f"Extracting playlist: {playlist_name}...")
    all_tracks.extend(get_playlist_tracks(playlist_id, playlist_name))

# Extract saved albums
print("Extracting saved albums...")
all_tracks.extend(get_saved_albums())

# Convert to DataFrame
df = pd.DataFrame(all_tracks)

# Save as UTF-8 CSV with correct formatting
csv_filename = "spotify_playlists_and_albums.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)

print(f"✅ Export complete! Data saved as '{csv_filename}'.")
