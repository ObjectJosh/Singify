<h1 align="center">
  <br>
  Singify
</h1>
<p align="center">
  Introducing Singify, the party game! Challenge your friend to who knows songs better. Play random songs from your very own Spotify playlist and duel friends to see who can finish the lyrics first!
</p>
<p align="center">
  <a href="https://devpost.com/software/singify?ref_content=my-projects-tab&ref_feature=my_projects">
    <img alt="RE: SLO Hacks Winner" src="https://img.shields.io/badge/RE%3A%20SLO%20Hacks-winner-brightgreen?style=flat-square">
    <img alt="GitHub language count" src="https://img.shields.io/github/languages/count/ObjectJosh/Singify?color=blueviolet&style=flat-square">
    <img alt="Github line count" src="https://img.shields.io/tokei/lines/github/ObjectJosh/Singify?style=flat-square">
    <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/ObjectJosh/Singify?color=orange&style=flat-square">
<!--     <img src="https://img.shields.io/github/languages/code-size/ObjectJosh/Singify?style=flat-square"> -->
  </a>
  
</p>
<h5 align="center">
  <a href="#about">About</a> •
  <a href="#tools-and-dependencies">Tools and Dependencies</a> •
  <a href="#getting-started">Getting Started</a>
</h5>

---

<h4 align="center">

  **First place winner of <a href="https://re-slo-hacks.devpost.com/" target="_blank">RE: SLO Hacks</a> Hackathon**
  <br>
  <br>
  **Devpost Submission: <a href="https://devpost.com/software/singify?ref_content=my-projects-tab&ref_feature=my_projects" target="_blank">Singify</a>**

</h4>

---

<br />

# About

### How to Play
A two-player game for you and your friends! After telling Singify which playlist you would like to play from, it will choose a random song and start playing a random part of the song for a few seconds, then stop it. Once the song stops, Singify uses visual artificial intelligence to detect who raised their hand first, and allow them to finish the lyrics. If the player gets it wrong, it's the next player's turn to give it a try. Once the point is given, Singify plays the next song. See who is the lyrical genius!

<br />

### Description
We used machine learning to detect human poses for raising hands, which we trained using our own recorded pose data. A pose uses a body's position in a live camera feed to set skeletal landmark points, which we used to recognize if your hand is up or not. We used speech recognition to take user voice input and parse the speech through pattern matching, and detect matches with the corresponding song lyrics.

<br />

### Tools and Dependencies
- Spotify API
- YouTube Search API
- YouTube Transcript API
- SF Speech Recognizer
- Google Teachable Machine
- Python Levenshtein

<br />

### Our Team
| <a href="https://github.com/ObjectJosh" target="_blank"><img src="https://avatars.githubusercontent.com/u/42549561?v=4" width="125px"/></a> | <a href="https://github.com/chonein" target="_blank"><img src="https://avatars.githubusercontent.com/u/61818445?v=4" width="125px"/></a> | <a href="https://github.com/Westluu" target="_blank"><img src="https://avatars.githubusercontent.com/u/76977316?v=4" width="125px"/></a> | <a href="https://github.com/wiszeto" target="_blank"><img src="https://avatars.githubusercontent.com/u/85478086?v=4" width="125px"/></a> |
|     :---:      |       :---:      |      :---:      |     :---:     |
| **Josh Wong** <br /> *Developer* | **Christian Honein** <br /> *Developer* |  **Wesley Luu** <br /> *Developer* | **Wilson Szeto** <br /> *Developer* |

<br />
<br />

# Getting Started
### Requirements
- **Spotify Premium**
  - *(this is essential, as you can't perform functional features of this app with a Spotify Free Account)*
- `pip` or `pip3`

### Installing Dependencies
- youtube-transcript-api
- youtube-search
- fuzzywuzzy
- python-Levenshtein
```
pip3 install youtube-transcript-api youtube-search fuzzywuzzy python-Levenshtein
```

## Run the App
    git clone https://github.com/ObjectJosh/Singify.git

**Install <a href="#installing-dependencies">Dependencies</a> *(see above)***

    cd Singify

**Make folder named** `store` **and create a blank** `store.txt` **file in it**

### Setting up Spotify API Authorization:
- Set up a new <a href="https://developer.spotify.com/dashboard/login" target="_blank">Spotify Developer Project</a>
- Set Redirect URI: https://github.com/ObjectJosh and `Save`
- `Copy` Client ID and `Paste` into first line of `store.txt`
- Click `SHOW CLIENT SECRET`
- `Copy` Client Secret and `Paste` into second line of `store.txt`
- Save the file (`store.txt`)

**In terminal, make sure you are in the** `/Singify` **directory and:**

    python3 game.py
   - *(or `python` or `py`)*

**A page should automatically open in the browser.** `Copy` **that URL and** `Paste` **into current terminal**

**Upon success, all further runs of the program can be started using:**

    python3 game.py
   - *(or `python` or `py`)*
