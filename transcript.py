from youtube_transcript_api import YouTubeTranscriptApi
import re
from youtube_search import YoutubeSearch
import config

THOUSAND = 1000
MINUTE = 60

def seconds_to_mili(seconds):
    """
    args:
    second - string in 3:56 format
    """
    if seconds.count(":") == 0:
        secs = int(seconds)
        return secs * THOUSAND
    if seconds.count(":") == 1:
        col_index = seconds.find(":")
        secs = int(seconds[col_index+1:])
        mins = int(seconds[0:col_index])
        return mins * (MINUTE * THOUSAND) + secs * THOUSAND

def get_video_id(search_term, spotify_duration):
    # searches for videos on youtube and gets dic
    video_info = []
    # dictionary of video info
    results = YoutubeSearch(search_term, max_results=config.NUMBER_OF_SEARCH_RESULTS).to_dict()
    # parse list of dictionary that contains videos id and duration from dic
    for dict_item in results:
        if dict_item["duration"].count(":") >= 2:
            continue
        if spotify_duration * 0.8 <= seconds_to_mili(dict_item["duration"]) <= spotify_duration * 1.5:
            video_info.append({
                "id": dict_item["id"],
                "duration": seconds_to_mili(dict_item["duration"])
            })
    # tests if a video has a trasnscript
    video_id = ""
    for idx, vid_id in enumerate(video_info):
        video_id = vid_id["id"]
        try:
            transcript_raw = YouTubeTranscriptApi.get_transcript(video_id)
            break
        except:
            print(f"No transcript found for this video ({idx + 1}/{len(video_info)})")
            transcript_raw = []
    # makes all lyrics text lowercase and from a-z A-z 0-9
    for item in transcript_raw:
        item["text"] = re.sub(r'[^a-zA-Z0-9_ ]', '', item["text"]).lower()
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
    
def get_frame(lyric_arr, start_time):
    """ Performs binary search to find subarry of lyrics according to time
    """
    # Convert time from milliseconds to seconds
    start_time = (start_time / THOUSAND) + config.FRAME_SHIFT
    first = 0
    last = len(lyric_arr) - 1
    time_tolerance = config.TIME_TOLERANCE_INCREMENT
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
        if not found and time_tolerance > config.MAXIMUM_TOLERANCE:
            print("Error: Middle index not found")
            return False
        # CASE current tolerance was not enough, increase the time tilerance
        elif not found:
            time_tolerance += config.TIME_TOLERANCE_INCREMENT
    # Closest matching item in the transcript list has been found
    # Create a subarray of items before and after
    transcript_frame = [found]
    scan_left = mid - 1
    scan_right = mid + 1
    total_duration = found["duration"]
    while scan_left and scan_right:
        if scan_left and scan_left >= 0 and abs(lyric_arr[scan_left]["duration"]) + total_duration <= config.FRAME_DURATION:
            # Add item to beginning of the list
            transcript_frame.insert(0, lyric_arr[scan_left])
            total_duration += abs(lyric_arr[scan_left]["duration"])
            scan_left -= 1
        else:
            scan_left = False
        # Might need to change to len instead of len - 1
        if scan_right and scan_right < len(lyric_arr) - 1 and abs(lyric_arr[scan_right]["duration"]) + total_duration <= config.FRAME_DURATION:
            # Add item to end of the list
            transcript_frame.append(lyric_arr[scan_right])
            total_duration += abs(lyric_arr[scan_right]["duration"])
            scan_right += 1
        else:
            scan_right = False
    # The transcript frame has been made
    return transcript_frame

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