import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# Function to read configuration from a text file
def read_config(filename='config.txt'):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config

# Read configuration
config = read_config()

# Spotify API credentials and settings
CLIENT_ID = config['CLIENT_ID']
CLIENT_SECRET = config['CLIENT_SECRET']
REDIRECT_URI = config['REDIRECT_URI']
TARGET_PLAYLIST_ID = config['TARGET_PLAYLIST_ID']
SCOPE = 'user-library-read user-library-modify playlist-modify-public playlist-modify-private'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

def get_liked_songs():
    results = sp.current_user_saved_tracks(limit=50)
    liked_songs = results['items']
    return liked_songs

def add_song_to_playlist(song_id, playlist_id):
    sp.playlist_add_items(playlist_id, [song_id])

def remove_song_from_liked(song_id):
    sp.current_user_saved_tracks_delete([song_id])

def main():
    processed_songs = set()  # To keep track of already processed songs

    while True:
        try:
            liked_songs = get_liked_songs()
            
            for item in liked_songs:
                song_id = item['track']['id']
                if song_id not in processed_songs:
                    add_song_to_playlist(song_id, TARGET_PLAYLIST_ID)
                    remove_song_from_liked(song_id)
                    processed_songs.add(song_id)
                    print(f"Moved {item['track']['name']} to target playlist and removed from liked songs.")
            
            time.sleep(60)  # Check every 60 seconds

        except KeyboardInterrupt:
            print('KeyboardInterrupt by user in main')
            break

if __name__ == '__main__':
    main()
