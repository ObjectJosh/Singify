from youtube_transcript_api import YouTubeTranscriptApi
import re
from youtube_search import YoutubeSearch

def seconds_to_mili(seconds):
    """
    args:
    second - string in 3:56 format
    """
    if seconds.count(":") == 0:
        secs = int(seconds)
        return secs*1000
    elif seconds.count(":") == 1:
        col_index = seconds.find(":")
        secs = int(seconds[col_index+1:])
        mins = int(seconds[0:col_index])
        return mins*60000 + secs*1000

def get_video_id(search_term, spotify_duration):
    #searches for videos on youtube and gets dic
    numb_of_search = 10
    video_info = []
    results = YoutubeSearch(search_term, max_results=numb_of_search).to_dict()
    #print(results) #dictionary of video info
    #parse list of dictionary that contains videos id and duration from dic
    for dic in results:
        if dic["duration"].count(":") >= 2:
            continue
        if spotify_duration * 0.8 <= seconds_to_mili(dic["duration"]) <= spotify_duration * 1.5:
            video_info.append({
                "id": dic["id"],
                "duration": seconds_to_mili(dic["duration"])
            })
    #print(video_info)
    #print(video_info)


    #tests if a video has a trasnscript
    video_id = ""
    for vid_id in video_info:
        video_id = vid_id["id"]
        try:
            x = YouTubeTranscriptApi.get_transcript(video_id)
            break
        except:
            print("no transcript for this video")
            x = []
        
    #makes all lyrics text lowercase and from a-z A-z 0-9
    for i in x:
        i["text"] = re.sub(r'[^a-zA-Z0-9_ ]', '',i["text"] ).lower()
        #print(i)
    print(video_id)
    return video_id

def get_transcript(code):
    """
    Format of an item in the transcript:
    {
        "text": "♪ Sometimes all I\nthink about is you ♪",
        "start": 30.833,
        "duration": 2.833
    }
    """
    print("Getting transcript... ", end="")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(code)
        print("Success")
        if transcript:
            return transcript
        raise Exception
    except:
        print("Failed")
        return False

if __name__ == "__main__":
    # For testing
    intentional = True
    if intentional:
        transcript = get_transcript("mRD0-GxqHVo")
        if transcript:
            for line in transcript:
                print(line)
            print("Done\n\n")
    else:
        print("Error: Please run from main.py")
        print("Usage: python3 main.py")