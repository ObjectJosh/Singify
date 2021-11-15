import speech
import subprocess as sp
from player import Player

class Game:
    def __init__(self) -> None:
        self.speechRecognizer = speech.Speech(2)
        self.player_left = self.init_player("left")
        self.player_right = self.init_player("right")

    def init_player(self, player_side: str):
        say(f"Player on the {player_side} side, what is your name?")
        player = Player(self.speechRecognizer.startSpeechRecognition(5))
        while player.name == '' or player.name.count(' ') + 1 > 2:
            print(f'Error in given name {player.name}')
            say("Sorry, I didn't quite catch that, can you repeat?")    
            player = Player(self.speechRecognizer.startSpeechRecognition(5))
        print(player.name)
        say(f'nice to meet you {player.name}!')
        return player


def say(text: str):
    sp.call(['say', text])

if __name__ == '__main__':
    game = Game()
