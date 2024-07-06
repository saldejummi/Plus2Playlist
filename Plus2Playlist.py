import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests.exceptions
import os
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

# Remove cached token to force reauthorization
if os.path.exists('.cache'):
    os.remove('.cache')

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

# Retry decorator
@retry(stop=stop_after_attempt(7), wait=wait_exponential(multiplier=1, min=4, max=64), retry=(retry_if_exception_type(requests.exceptions.RequestException)))
def get_liked_songs():
    results = sp.current_user_saved_tracks(limit=50)
    return results['items']

@retry(stop=stop_after_attempt(7), wait=wait_exponential(multiplier=1, min=4, max=64), retry=(retry_if_exception_type(requests.exceptions.RequestException)))
def add_song_to_playlist(song_id):
    sp.playlist_add_items(TARGET_PLAYLIST_ID, [song_id])

@retry(stop=stop_after_attempt(7), wait=wait_exponential(multiplier=1, min=4, max=64), retry=(retry_if_exception_type(requests.exceptions.RequestException)))
def remove_song_from_liked(song_id):
    sp.current_user_saved_tracks_delete([song_id])  

def main():
    print('Scanning liked songs every 60 seconds...')
    while True:
        try:
            liked_songs = get_liked_songs()
            for item in liked_songs:
                song_id = item['track']['id']
                add_song_to_playlist(song_id)
                remove_song_from_liked(song_id)
                print(f"Moved {item['track']['name']} to target playlist and removed from liked songs.")
            time.sleep(60)  # Check every 60 seconds
        except KeyboardInterrupt:
            print('KeyboardInterrupt by user in main')
            break
        except Exception as e:
            print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
