from subprocess import Popen
import sys
import random
import os
import time
import threading
from fuzzywuzzy import fuzz
from typing import Optional
import webbrowser

# File imports
import speech
from player import Player
import transcript
from spotify import Spotify
from utilities import say, simplify_string
import config
from hand_status import HandRaise

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

class Game:
    def __init__(self) -> None:
        self.spotify = self.init_spotify_auth()
        self.speechRecognizer = speech.Speech()
        self.https_process = Popen(['python', 'http_server.py'])
        webbrowser.open_new_tab("http://localhost:8000/tri-halves.html")
        self.play_introduction()
        self.player_left = self.init_player("left")
        self.player_right = self.init_player("right")
        self.playlist = self.init_playlist()
        self.current_track = None
        self.lyrics = ""
        self.track_seek_time = None
        self.hand_raise = HandRaise()
        # We can use this to see, for example, if a player raised their hand first 3 times in a row,
        # the computer says, "Player [ ] again? Wow, you're quick!"
        self.raised_hand_log = []
        self.start()
    
    # def start_http_server(self):
    #     process = Popen(['python', 'http_server.py'])
    
    def play_introduction(self):
        print("Welcome to Singify! Say 'Play' to start, or you can say 'Tell me the rules'")
        say("Welcome to Sinify! Say 'Play' to start, or you can say 'Tell me the rules'")
        ret = simplify_string(self.speechRecognizer.startSpeechRecognition(3))
        if ret in ["play", "start", "begin", "go"] or "play" in ret:
            print("Alright, let's begin!")
            say("Alright, let's begin!")
        elif ret in ["rules", "tell me the rules", "what are the rules", "the rules", "play the rules"] or "rules" in ret:
            msg = "The goal of this game is to finish the lyrics after I play \
                a part of a song. You only need to tell me about five words. \
                After giving me a playlist, I will play a random track in \
                that playlist and skip to a random time, playing ten seconds \
                of the track. When I pause the track, the first person to \
                raise their hand will guess first. If that player gets it \
                wrong, the second player can give it a try."
            print(msg)
            say(msg)
            say("Shall we begin?")
            ret = simplify_string(self.speechRecognizer.startSpeechRecognition(2))
            if ret in ["yes", "play", "start", "begin", "go"]:
                print("Alright, let's begin!")
                say("Alright, let's begin!")
            else:
                print("Goodbye!")
                say("Goodbye!")
                exit()
        else:
            self.play_introduction()

    def start(self):
        playing = True
        while playing:
            self.play_random_track()
            threading.Thread(target=self.get_track_transcript_lyrics).start()
            self.pause_track_in(seconds=10)
            self.detect_hand_raise() # Detects hand raise and lets players guess
        print("Goodbye! Thanks for playing!")
        say("Goodbye! Thanks for playing!")

    def init_spotify_auth(self):
        if os.path.exists("store/store.txt"):
            id, sec, token = self.receive_keys()
            spotify = Spotify(id, sec, token)
        else:
            spotify = Spotify()
        spotify.authenticate()
        # Pause Spotify if it's playing right now
        if spotify.status()["is_playing"]:
            spotify.pause()
            print("A song was already playing. The song has been paused")
        return spotify
    
    def receive_keys(self):
        with open("store/store.txt", "r") as f:
            l = [None] * 3
            for idx, line in enumerate(f):
                if line.strip() != "":
                    l[idx] = line.strip()
                if idx >= 2:
                    break
            return tuple(l)

    def init_player(self, player_side: str) -> Optional[Player]:
        say(f"Player on the {player_side} side, what is your name?")
        player = Player(self.speechRecognizer.startSpeechRecognition(2))
        false_counter = 0
        while false_counter < 3 and\
                (player.name == '' or player.name.count(' ') + 1 > 2):
            print(f"Error in given name {player.name}")
            say("Sorry, I didn't quite catch that, can you repeat your name?")
            player = Player(self.speechRecognizer.startSpeechRecognition(2))
            false_counter += 1
        if false_counter > 3:
            say("This doesn't seem to be working, please try again later.")
            sys.exit()
        print(player.name)
        say(f'Nice to meet you {player.name}!')
        return player
    
    def init_playlist(self):
        # Asks user for playlist until the given playlist is valid
        playlist_found = False
        while not playlist_found:
            playlist_found, playlist = self.ask_for_playlist()
        say(f"Playing your {playlist['name']} playlist...")
        print(f"Playing your {playlist['name']} playlist...")
        return playlist
    
    def ask_for_playlist(self):
        say(f"Which playlist would you like? ")
        request = self.speechRecognizer.startSpeechRecognition(4)
        ret = self.spotify.get_playlist(request)
        # Handle ret output
        # CASE: Error: specified playlist is empty
        # CASE: Error: specified playlist has no matches in your playlists
        if ret == -1 or ret == -2:
            valid, ret = self.handle_playlist_request_error(ret)
            return valid, ret
        # CASE: When ret is a list, it means that ret has a list of playlist dicts that may have been a match
        # Ask the user which one they want, or none of them
        elif isinstance(ret, list):
            valid, ret = self.handle_playlist_possible(ret)
            return valid, ret
        # CASE: ret is a playlist dict
        elif isinstance(ret, dict):
            return True, ret
        return False, None
    
    def handle_playlist_request_error(self, ret):
        if ret == -1:
            print("Error: specified playlist is empty")
            say("Sorry, that playlist was empty")
        elif ret == -2:
            print("Error: specified playlist has no matches in your playlists")
            say("Sorry, that playlist doesn't match and playlist in your library")
        # TODO More error handling (like asking again, or if they want a random track instead)
        say("Do you want to ask again or play a random playlist instead? ")
        ret = simplify_string(self.speechRecognizer.startSpeechRecognition(3))
        # ret = input("Do you want to ask again or play a random playlist instead? ")
        if ret == "ask again":
            return False, None
        elif ret in ["random", "play random", "play a random song", "whatever"]:
            ret = self.spotify.get_playlist()
            return True, ret
        return False, None
    
    def handle_playlist_possible(self, ret):
        names = []
        for each in ret:
            names.append(simplify_string(each["name"]))
        toggle_response = True
        random = False
        while ret not in names and not random:
            if toggle_response:
                say(f"I found {names} as matches. Which one did you mean? ")
                ret = simplify_string(self.speechRecognizer.startSpeechRecognition(5))
                toggle_response = not toggle_response
            else:
                say("Sorry, please try again, or you could tell me to play a random one ")
                ret =simplify_string(self.speechRecognizer.startSpeechRecognition(4))
            if ret in ["random", "play random", "play a random song", "whatever"]:
                random = True
        if not random:
            return True, self.spotify.get_playlist(ret)
        return True, self.spotify.get_playlist()
    
    def play_random_track(self):
        # Valid playlist, now we get the tracks
        tracks = self.spotify.get_tracks(self.playlist["tracks"])
        self.current_track = random.choice(tracks)

        # Once a random track is found, add it to the queue and skip to it
        print(f"Adding {self.current_track['name']} to the queue...")
        self.spotify.add_to_queue(self.current_track)
        self.spotify.skip()
        # Seek to a random time on the song
        self.track_seek_time = self.spotify.get_random_time(self.current_track)
        success = self.spotify.seek(self.track_seek_time, self.current_track)
        while not success:
            # random_time = spotify.get_random_time(random_track)
            success = self.spotify.seek(self.track_seek_time, self.current_track)
            if not success:
                print("Trying again...")
    
    def get_track_transcript_lyrics(self):
        # Given Song Title and Artist, input into transcript finder
        transcript = self.get_transcript_frame()
        if transcript:
            for i in transcript:
                self.lyrics = self.lyrics + " " + i["text"]
        else:
            say("Sorry, I wasn't able to get lyrics to match to that song")
            print("Error: Unable to get lyrics")
    
    def get_transcript_frame(self):
        video_id = transcript.get_video_id(self.current_track["name"], self.current_track["duration"])
        lyric_arr = transcript.get_transcript(video_id)
        if lyric_arr:
            return transcript.get_frame(lyric_arr, self.track_seek_time)
        return False
    
    def pause_track_in(self, seconds):
        # Pauses the track currently playing in (user inputted) seconds
        start_time = time.time()
        time_diff = time.time() - start_time < seconds
        while time_diff:
            time_diff = time.time() - start_time < seconds
        print("Pausing song....")
        self.spotify.pause()
    
    def detect_hand_raise(self):
        print("Detecting hand raise...")
        val = 'low'
        while val == 'low':
            val = self.hand_raise.get_first_hand_raiser()
            print(val)
        # HARD CODED
        print(val)
        if val == 'left':
            raised_hand_player = self.player_left
            self.raised_hand_log.append(self.player_left)
        else:
            raised_hand_player = self.player_right
            self.raised_hand_log.append(self.player_right)
        say(f"{raised_hand_player.name} raised their hand first!")
        self.handle_hand_raise()

    def handle_hand_raise(self):
        # Determine which player raised their hand first (whose turn it is)
        if self.raised_hand_log[-1] == self.player_left:
            first_guesser = self.player_left
            second_guesser = self.player_right
        else:
            first_guesser = self.player_right
            second_guesser = self.player_left
        # Hand raise was detected, get user input, which is their guess
        user_input = self.handle_user_lyric_guess()
        if user_input:
            potential = self.match_guess_to_lyrics(user_input)
            if potential: # Developer use 
                print(potential) # Developer use
            # Handle if the guess was correct, if returns True, first player was correct
            # and no need to ask the second player
            if self.handle_lyric_correctness(potential, first_guesser):
                return
        # Second player's turn
        say(f"{second_guesser.name}, your turn to try.")
        user_input = self.handle_user_lyric_guess()
        if user_input:
            potential = self.match_guess_to_lyrics(user_input)
            print(potential) # Developer use
            self.handle_lyric_correctness(potential, second_guesser)
    
    def handle_lyric_correctness(self, potential, player):
        if potential:
            for each in potential: # Developer use
                print(each) # Developer use
            say("That's correct!")
            print("That's correct!")
            # Give a point to the player who raised their hand
            player.score += 1
            # Point given, don't let second player guess
            return True
        say("Sorry! That wasn't correct!")
        print("Sorry! That wasn't correct!")
        return False
    
    def handle_user_lyric_guess(self):
        user_input = self.speechRecognizer.startSpeechRecognition(10)
        say("Time's up!")
        print("User input received:") # Developer use
        print(user_input) # Developer use
        # Remove raw input that is too short to be accepted
        if len(user_input) > 20:
            return user_input
        say("Sorry! That was too short")
        return False
    
    def match_guess_to_lyrics(self, user_input):
        potential = []
        for idx, char in enumerate(self.lyrics):
            if char == ' ':
                lyric_sub = self.lyrics[idx : idx + len(user_input)]
                ratio = fuzz.ratio(user_input, lyric_sub)
                if ratio > config.LYRIC_MATCH_PERCENT:
                    potential.append(lyric_sub)
            # Prevent index out of bounds when matching lyrics
            if idx > len(self.lyrics) - len(user_input) - 2:
                break
        return potential
    
    # Commands (function below is not used for the program, just for reference)
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

if __name__ == '__main__':
    game = None
    try:
        game = Game()
    except KeyboardInterrupt:
        if game is not None:
            game.https_process.terminate()
        raise KeyboardInterrupt()
