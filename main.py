import os
import random
from spotify import Spotify, simplify_string
from lyrics import swag_lyrics
import transcript
import time
from fuzzywuzzy import fuzz

#|##########################################################################|#
#|                                  SETUP                                   |#
#|##########################################################################|#
    # (1) in terminal, `pip3 install requests`
    # (2) create/add a file in the "store" folder named "store.txt"
    # (3) go to https://developer.spotify.com/dashboard/login
    #       (1) login
    #       (2) create an app
    #       (3) copy Client ID and paste into first line of "store.txt"
    #       (4) click "SHOW CLIENT SECRET"
    #       (5) copy Client Secret and paste into second line of "store.txt"
    #       (6) save the file ("store.txt")
    # (4) in terminal, `python3 main.py`

# ENVIRONMENT VARIABLES
FRAME_DURATION = 40 # (seconds)
FRAME_SHIFT = 0 # (seconds) can be positive or negative
TIME_TOLERANCE_INCREMENT = 5 # (seconds)
MAXIMUM_TOLERANCE = 20 # (seconds)


def setup():
    if os.path.exists("store/store.txt"):
        id, sec, token = receive_keys()
        spotify = Spotify(id, sec, token)
    else:
        spotify = Spotify()
    spotify.authenticate()
    # Pause Spotify if it's playing right now
    if spotify.status()["is_playing"]:
        spotify.pause()
        print("A song was already playing. The song has been paused")
    return spotify

def run(spotify):
    playlist_found = False
    while not playlist_found:
        playlist_found, playlist = ask_for_playlist(spotify)
    print(f"Playing your {playlist['name']} playlist...")
    # Valid playlist, now we get the tracks
    tracks = spotify.get_tracks(playlist["tracks"])
    random_track = random.choice(tracks)

    # Once a random track is found, add it to the queue and skip to it
    print(f"Adding {random_track['name']} to the queue...")
    spotify.add_to_queue(random_track)
    spotify.skip()
    # lyrics = swag_lyrics.lyrics(random_track["name"], random_track["artists"][0])
    # print(lyrics)
    # Seek to a random time on the song
    random_time = spotify.get_random_time(random_track)
    success = spotify.seek(random_time, random_track)
    while not success:
        random_time = spotify.get_random_time(random_track)
        success = spotify.seek(random_time, random_track)
        if not success:
            print("Trying again...")
    start_time = time.time()
    # Given Song Title and Artist, input into transcript finder
    transcript = get_transcript_frame(random_track["name"], random_track["duration"], random_time)
    if transcript:
        pass
        # for each in transcript:
        #     print(each)
    else:
        print("Error: Unable to get lyrics")
    # time_diff = time.time() - start_time < 10
    # while time_diff:
    #     time_diff = time.time() - start_time < 10
    # print("Time's up!")
    # spotify.pause()
    lyrics = ""
    for i in transcript:
        lyrics = lyrics + " " + i["text"]
    print(lyrics)
    user_input = "You look so broken when you cry One more and then I'll say goodbye"
    user_input = lyrics[10:50]
    print(user_input)
    potential = []
    for idx, char in enumerate(lyrics):
        if char == ' ':
            lyric_sub = lyrics[idx : idx + len(user_input)]
            ratio = fuzz.ratio(user_input, lyric_sub)
            if ratio > 80:
                potential.append(lyric_sub)
        if idx > len(lyrics) - len(user_input) - 5:
            break
    print(potential)
    if potential:
        for each in potential:
            print(each)
        print("Correct!")
    else:
        print("Sorry! That wasn't correct!")
    # playing = True
    # while playing:
    #     playing = ask_for_command(spotify)


def ask_for_playlist(spotify):
    request = input("Which playlist would you like? ")
    ret = spotify.get_playlist(request)
    # Parse return
    # CASE: Error: specified playlist is empty
    # CASE: Error: specified playlist has no matches in your playlists
    if ret == -1 or ret == -2:
        if ret == -1:
            print("Error: specified playlist is empty")
        elif ret == -2:
            print("Error: specified playlist has no matches in your playlists")
        # TODO More error handling (like asking again, or if they want a random track instead)
        ret = input("Do you want to ask again or play a random playlist instead? ")
        if ret == "ask again":
            return False, None
        elif ret in ["random", "play random", "play a random song", "whatever"]:
            ret = spotify.get_playlist()
            return True, ret
        return False, None
    # CASE: When ret is a list, it means that ret has a list of playlist dicts that may have been a match
    # Ask the user which one they want, or none of them
    elif isinstance(ret, list):
        names = []
        for each in ret:
            names.append(simplify_string(each["name"]))
        toggle_response = True
        random = False
        while ret not in names and not random:
            if toggle_response:
                ret = simplify_string(input(f"I found {names} as matches. Which one did you mean? "))
                toggle_response = not toggle_response
            else:
                ret = simplify_string(input("Sorry, please try again, or you could tell me to play a random one "))
            if ret in ["random", "play random", "play a random song", "whatever"]:
                random = True
        return True, ret
    # CASE: ret is a playlist dict
    elif isinstance(ret, dict):
        return True, ret
    return False, None

def ask_for_command(spotify):
    request = input("Let's begin! What would you like to do? ")
    if request == "seek":
        duration = input("Time(ms): ")
        spotify.seek(duration) # Example: 20000 = 20 seconds
    elif request == "pause":
        spotify.pause()
    elif request == "play":
        spotify.play()
    elif request == "skip":
        spotify.skip()
    elif request in ["exit", "stop", "cancel", "quit"]:
        spotify.pause()
        print("Thanks for playing!")
        return False
    return True

def receive_keys():
    with open("store/store.txt", "r") as f:
        l = [None] * 3
        for idx, line in enumerate(f):
            if line.strip() != "":
                l[idx] = line.strip()
            if idx >= 2:
                break
        return tuple(l)

def get_transcript_frame(track_name, track_duration, start_time):
    # video_code = transcript.
    # video_code = "mRD0-GxqHVo"
    # video_code = "XbGs_qK2PQA"
    video_id = transcript.get_video_id(track_name, track_duration)
    lyric_arr = transcript.get_transcript(video_id)
    return get_frame(lyric_arr, start_time)

def get_frame(lyric_arr, start_time):
    """ Performs binary search to find subarry of lyrics according to time
    """
    # Convert time from milliseconds to seconds
    start_time = (start_time / 1000) + FRAME_SHIFT
    first = 0
    last = len(lyric_arr) - 1
    time_tolerance = TIME_TOLERANCE_INCREMENT
    found = False
    mid = 0
    while not found:
        while (first <= last):
            mid = (first + last) // 2
            mid_start_time = lyric_arr[mid]["start"]
            time_difference = abs(start_time - mid_start_time)
            if time_difference <= time_tolerance:
                found = lyric_arr[mid]
                break
            elif start_time < mid_start_time:
                last = mid - 1
            else:
                first = mid + 1
        # CASE no matching lyrics found with maximum second tolerance
        if not found and time_tolerance > MAXIMUM_TOLERANCE:
            print("Error: Middle index not found")
            return False
        # CASE current tolerance was not enough, increase the time tilerance
        elif not found:
            time_tolerance += TIME_TOLERANCE_INCREMENT
    # Closest matching item in the transcript list has been found
    # Create a subarray of items before and after
    transcript_frame = [found]
    scan_left = mid - 1
    scan_right = mid + 1
    total_duration = found["duration"]
    while scan_left and scan_right:
        if scan_left and scan_left >= 0 and abs(lyric_arr[scan_left]["duration"]) + total_duration <= FRAME_DURATION:
            # Add item to beginning of the list
            transcript_frame.insert(0, lyric_arr[scan_left])
            total_duration += abs(lyric_arr[scan_left]["duration"])
            scan_left -= 1
        else:
            scan_left = False
        # Might need to change to len instead of len - 1
        if scan_right and scan_right < len(lyric_arr) - 1 and abs(lyric_arr[scan_right]["duration"]) + total_duration <= FRAME_DURATION:
            # Add item to end of the list
            transcript_frame.append(lyric_arr[scan_right])
            total_duration += abs(lyric_arr[scan_right]["duration"])
            scan_right += 1
        else:
            scan_right = False
    # The transcript frame has been made
    return transcript_frame

if __name__ == '__main__':
    spotify = setup()
    run(spotify)