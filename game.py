import speech
import subprocess as sp
from player import Player
from typing import Optional
import sys
import main
import random


class Game:
    def __init__(self) -> None:
        self.speechRecognizer = speech.Speech(2)
        self.player_left = self.init_player("left")
        self.player_right = self.init_player("right")
        # self.playlist = self.init_playlist()
        # self.spotify = Spotify()

    def init_player(self, player_side: str) -> Optional[Player]:
        say(f"Player on the {player_side} side, what is your name?")
        player = Player(self.speechRecognizer.startSpeechRecognition(5))
        false_counter = 0
        while false_counter < 3 and\
                (player.name == '' or player.name.count(' ') + 1 > 2):
            print(f'Error in given name {player.name}')
            say("Sorry, I didn't quite catch that, can you repeat?")
            player = Player(self.speechRecognizer.startSpeechRecognition(5))
            false_counter += 1
        if false_counter > 3:
            say("This doesn't seem to be working, please try again later.")
            sys.exit()
        print(player.name)
        say(f'nice to meet you {player.name}!')
        return player


def say(text: str) -> None:
    sp.call(['say', text])


if __name__ == '__main__':
    spotify = main.setup()
    game = Game()
    main.run(spotify)
    
# FOR JOSH COPY PASTE:
# self.speechRecognizer.startSpeechRecognition(5)
# def say(text: str) -> None:
#     sp.call(['say', text])
