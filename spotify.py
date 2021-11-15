from json.decoder import JSONDecodeError
import os
import requests
import re
import datetime
import base64
import json
import urllib.parse
import random
import time

API_PLAYER_URL = "https://api.spotify.com/v1/me/player"
API_PLAYLIST_URL = "https://api.spotify.com/v1/users/pgro68ovwg36mhhjq2jastwv0/playlists"
API_TOKEN_URL = "https://accounts.spotify.com/api/token"
API_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
REDIRECT_URL = "https://github.com/ObjectJosh"


class Spotify(object):
    def __init__(self, client_id=None, client_sec=None, refresh_token=None):
        self.id = client_id
        self.sec = client_sec
        self.refresh_token = refresh_token
        self.access_token_expiration = None
        self.access_token_did_expire = True
    
    def authenticate(self):
        # HARD CODED FOR NOW
        authenticated = True
        if not self.refresh_token or not authenticated:
            self.handle_initial_authentication()
        refresh_handler = Refresh(self.refresh_token, self.get_credentials())
        self.access_token = refresh_handler.refresh(self)
        # self.check_authentication_status()
        # TODO refresh refresh_handler every hour with time
    
    def handle_initial_authentication(self):
        self.request_authorization()
        self.request_refresh_token()
        print("Authentication: Success")
    
    def check_authentication_status(self):
        token_headers = {
            "Authorization": f"Basic {self.get_credentials()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        token_data = {
            "grant_type": "authorization_code",
            "code": self.access_token,
            "redirect_uri": REDIRECT_URL
        }
        """
curl -H "Authorization: BASE64" -d grant_type=authorization_code -d code=CODE -d redirect_uri=https%3A%2F%2Fgithub.com%2FObjectJosh https://accounts.spotify.com/api/token
        """ 
        print(token_headers)
        print(token_data)
        RESPONSE = requests.post(API_TOKEN_URL, data=token_data, headers=token_headers)
        print(RESPONSE)
        if RESPONSE.status_code not in range(200, 299):
            print("Error: Could not authenticate user")
            exit()
        print("SUCCESS")
        request_json = RESPONSE.json()
        time_now = datetime.datetime.now()
        expires = time_now + datetime.timedelta(seconds=request_json["expires_in"])
        self.access_token = request_json["access_token"]
        self.access_token_expiration = expires
        self.access_token_did_expire = expires < time_now

    
    def request_refresh_token(self):
        print("\nPlease copy the URL that was opened in your browser and paste it below")
        auth_code = input("Paste URL Here: ")
        if auth_code.lower() in ["cancel", "stop", "exit", "leave", "quit"]:
            print("Goodbye!")
            exit()
        partioned = auth_code.partition("code=")[2]
        if partioned:
            auth_code = partioned
        URL = f"'Authorization: Basic {self.get_credentials()}' -d grant_type=authorization_code -d code={auth_code} -d redirect_uri={urllib.parse.quote(REDIRECT_URL)}"
        cmd = f"curl -H {URL} {API_TOKEN_URL}"
        str_output = os.popen(cmd).read()
        try:
            response_json = json.loads(str_output)
            self.refresh_token = response_json["refresh_token"]
        except:
            print("Error: Problem getting access token. Please check if the request or code was valid")
            exit()
        with open("store/store.txt", "w") as f:
            f.write(self.id + "\n")
            f.write(self.sec + "\n")
            f.write(self.refresh_token)
        print("Access token accepted")

    def request_authorization(self):
        scope = "user-read-playback-state+user-modify-playback-state+playlist-read-private"
        URL = f"{API_AUTHORIZE_URL}?client_id={self.id}&scope={scope}&response_type=code&redirect_uri={REDIRECT_URL}"
        RESPONSE = requests.get(URL)
        try:
            import webbrowser
            webbrowser.open(URL)
        except:
            print("Error: Something happened when trying to open url for authorization request")
            exit()
        if RESPONSE.status_code not in range(200, 299):
            print(f"Error: Something went wrong. Authorization request failed")
            try:
                ret = RESPONSE.json()["error"]
                print(f"Server message:\n\tError: {ret['status']}\n\tReason: {ret['message']}")
            except:
                pass
        RESPONSE.raise_for_status()

    def get_credentials(self):
        if self.id == None or self.sec == None:
            if self.id == None:
                print("No client id found")
            if self.sec == None:
                print("No client secret found")    
            print("Error: You must set both your client id and client secret first")
        credstr = f"{self.id}:{self.sec}"
        credb64 = base64.b64encode(credstr.encode())
        return credb64.decode()

    def get_access_token(self):
        if self.access_token_expiration < datetime.datetime.now():
            self.authenticate()
            return self.get_access_token()
        elif self.access_token == None:
            self.authenticate()
            return self.get_access_token() 
        return self.access_token


    def get_playlist(self, playlist_name = ""):
        """ Gets and returns user's specified playlist. If not specified, returns a random playlist
        Args:
            [optional] playlist_name(string): name of user's specified playlist
        Returns either:
            playlist(dict): dict containing playlist information from Spotify API
            potential(list): list of playlist dicts that may have been a match
            int: -1 on error, when specified playlist has no tracks in it
            int: -2 on error, when specified playlist has no matches or potential matches
        """
        # TODO set an offset so it's not always first 50 tracks picked
        # Because highest LIMIT you can request is 50 songs per call
        # Could this be solved by just using the SHUFFLE API request?
        LIMIT = 0
        if LIMIT > 0:
            URL = f"{API_PLAYLIST_URL}?limit={LIMIT}"
        else:
            URL = API_PLAYLIST_URL
        response_json = self.request_handler("GET", URL, "Playlists", "Playlists error: Check your connection to Spotify")
        PLAYLIST_NAME = simplify_string(playlist_name)
        playlists = []
        potential = []
        if "items" not in response_json or len(response_json["items"]) == 0:
            print("Error: No items found in your playlist library")
            exit()
        if PLAYLIST_NAME:
            for each in response_json["items"]:
                simplename = simplify_string(each["name"])
                # Add only playlists that have songs
                if each["tracks"]["total"] > 0:
                    playlist = {
                        "id": each["id"],
                        "name": each["name"],
                        "tracks": {
                            "link": each["tracks"]["href"],
                            "amount": each["tracks"]["total"]
                        }
                    }
                    # Requested playlist found, return single playlist
                    if PLAYLIST_NAME and simplename == PLAYLIST_NAME:
                        return playlist

                    # TODO Check for similar but not exact matches
                    # if similary_check(PLAYLIST_NAME, simplename)
                    # potential.append(playlist)

                    playlists.append(playlist)
                # Requested playlist found, but there are no tracks in the requested playlist (if requested)
                elif PLAYLIST_NAME and simplename == PLAYLIST_NAME:
                    return -1
            # User requested a playlist, but it was not found
            return -2
        # User did not specify a playlist, select a random one
        print("Selecting a random playlist...")
        return random.choice(playlists)

    def get_tracks(self, playlist_track):
        response_json = self.request_handler("GET", playlist_track["link"], "Tracks", "Tracks error: Check your connection to Spotify")
        tracks = []
        for each in response_json["items"]:
            cur = each["track"]
            artists = []
            for artist in cur["artists"]:
                artists.append(artist["name"])
            track = {
                "id": cur["id"],
                "name": cur["name"],
                "artists": artists,
                "link": cur["uri"],
                "duration": cur["duration_ms"]
            }
            tracks.append(track)
        if not tracks:
            print("Error: Something went wrong. No tracks found")
            exit()
        return tracks
    
    def add_to_queue(self, track):
        self.request_handler("POST", f"{API_PLAYER_URL}/queue?uri={track['link']}", "Add song to queue", "add to queue")
        print(f"Successfully added {track['name']} to the queue!")
    
    def seek(self, milliseconds, track=""):
        try:
            milliseconds = int(milliseconds)
        except ValueError:
            print("Error: Invalid seek input. Seek input is not an integer")
            exit()
        self.request_handler("PUT", f"{API_PLAYER_URL}/seek?position_ms={milliseconds}", "Seek song", "seek")
        print("Sleeping...", end="")
        time.sleep(2)
        print("Woke up")
        if track and self.status()["progress"] >= milliseconds:
            print(f"Seeked to {milliseconds / 1000} seconds")
            return True
        print("Seek failure")
        return False
    
    def pause(self):
        self.request_handler("PUT", f"{API_PLAYER_URL}/pause", "Pause song", "pause")

    def play(self):
        self.request_handler("PUT", f"{API_PLAYER_URL}/play", "Play song", "play")
    
    def skip(self):
        self.request_handler("POST", f"{API_PLAYER_URL}/next", "Skip song", "skip")
        print("Successfully skipped!")
    
    def status(self):
        response_json = self.request_handler("GET", API_PLAYER_URL, "Status", "Status error: Check your connection to Spotify")
        try:
            # Check if the json has "is_playing", "progress_ms", and "duration" fields
            status = {
                "is_playing": response_json["is_playing"],
                "progress": response_json["progress_ms"],
                "duration": response_json["item"]["duration_ms"]
            }
            return status
        except:
            print(f"Error: Could not detect a device playing Spotify. Try toggling play on Spotify and try again")
            exit()
    
    def get_random_time(self, track):
        # end of song buffer time (so it doesn't skip to a part in the end of the song)
        END_BUFFER = 20000
        return random.randint(0, track["duration"] - END_BUFFER)
    
    def request_handler(self, TYPE, URL, errmsg = "", opterrmsg = ""):
        if TYPE == "PUT":
            RESPONSE = requests.put(URL, headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        })
        elif TYPE == "POST":
            RESPONSE = requests.post(URL, headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        })
        elif TYPE == "GET":
            RESPONSE = requests.get(URL, headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        })
        else:
            print("Error: spotify.py: request_handler(): invalid argument for 'TYPE'")

        if opterrmsg and TYPE in ["PUT", "POST"]:
            opterrmsg = f"Song did not {opterrmsg}"
        response_json = check_error(RESPONSE, errmsg, opterrmsg)
        # For GET requests that have JSON with body, return it
        if response_json:
            return response_json

class Refresh:
    def __init__(self, refresh_token, base_64):
        self.refresh_token = refresh_token
        self.base_64 = base_64

    def refresh(self, spotify):
        response = requests.post(API_TOKEN_URL,
                                 data={"grant_type": "refresh_token",
                                       "refresh_token": self.refresh_token},
                                 headers={"Authorization": "Basic " + self.base_64})
        response_json = response.json()
        if "error" in response_json:
            print("There was something wrong with the refresh token. Prompting reauthentication...")
            spotify.handle_initial_authentication()
            return
        return response_json["access_token"]


def check_error(RESPONSE, errmsg = "", opterrmsg = ""):
    # Check response for error, first if it exists
    if RESPONSE is None:
        print("Error: No response found")
    code = RESPONSE.status_code
    if code not in range(200, 299):
        print(f"Error: Something went wrong. {errmsg}")
        try:
            ret = RESPONSE.json()["error"]
            print(f"Server message:\n\tError: {ret['status']}\n\tReason: {ret['message']}")
        except:
            pass
        if code == 401:
            print("API Token is invalid or has expired. Please generate a new token and try again. (See top of 'main.py')")
            exit()
    # Raise error status message if status is an error
    RESPONSE.raise_for_status()
    try:
        response_json = RESPONSE.json()
    # JSON has no contents, leave the function
    # Does not mean error, since some responses don't return content
    except JSONDecodeError:
        return
    try:
        # If there was an error message, print it
        if "error" in response_json:
            errno = response_json["error"]["status"]
            msg = response_json["error"]["message"]
            print(f"ERROR {errno}: {msg}")
            exit()
    except:
        print(f"Something went wrong. {opterrmsg}")
        exit()
    # Successfully parsed contents of response into JSON. Send back
    return response_json

def simplify_string(string):
    """ Removes punctuation and capitalization from given string
    Args:
        string(string): string to be simplified
    Returns:
        string: a string without punctuation or capitalization
    """
    return re.sub(r'[^a-zA-Z0-9]', '', string).lower()

if __name__ == "__main__":
    print("Error: Please run from main.py")
    print("Usage: python3 main.py")
