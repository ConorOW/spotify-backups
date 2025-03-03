import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Spotify API credentials (Replace with your details)
CLIENT_ID = "<CLIENT_ID>"
CLIENT_SECRET = "CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8888/callback"  # Default redirect URI

# Set up authentication with required scopes
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private user-library-read"  # Added 'user-library-read' to access saved albums
))

### Function to extract playlist tracks ###
def get_playlist_tracks(playlist_id, playlist_name):
    tracks = []
    results = sp.playlist_tracks(playlist_id)

    while results:
        for item in results['items']:
            track = item.get('track')  # Use .get() to prevent KeyError

            if track and 'external_urls' in track and 'spotify' in track['external_urls']:
                tracks.append({
                    'Type': 'Playlist',
                    'Playlist': playlist_name,
                    'Artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'Album': track['album']['name'],
                    'Title': track['name'],
                    'Track ID': track['id'],
                    'Track URL': track['external_urls']['spotify']  # Now safe
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
            album = item['album']
            albums.append({
                'Type': 'Saved Album',
                'Playlist': '',  # Not part of a playlist
                'Artist': ', '.join([artist['name'] for artist in album['artists']]),
                'Album': album['name'],
                'Title': '',  # No specific title since it's an album
                'Track ID': album['id'],
                'Track URL': album['external_urls']['spotify']
            })
        results = sp.next(results)  # Get next batch if available

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

# Convert to DataFrame and save as CSV
df = pd.DataFrame(all_tracks)
df.to_csv("spotify_playlists_and_albums.csv", index=False)

print("Export complete! Data saved as 'spotify_playlists_and_albums.csv'.")
