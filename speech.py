"""
This program calls the swift speech recognition code.
It takes its output.
At the moment, if we are detecting speech code is blocking.
This program requires stdbuf.
"""

from subprocess import Popen, PIPE
import time
import signal
# from typing import Optional
CMD = "transcribe/transcribe/./main"
PROCESS_RUNNING = False


class Speech:
    def __init__(self, stop_if_silent_time: int = 3, gstdbuf: bool = True)\
            -> None:
        """ on macos if installed using brew, stdbuf will be gstdbuf.
        If you have stdbuf, set gstdbuf to false.
        """
        self.stop_silent_t = stop_if_silent_time

    def startSpeechRecognition(self, detection_time: float,
                               stop_if_silent_time: int = None)\
            -> str:
        global PROCESS_RUNNING
        # runs compiled swift code using gstdbuf with argument -ol
        # this is to disable output buffers
        # gstdbuf only exists on MacOS using homebrew
        if stop_if_silent_time is None:
            stop_if_silent_time = self.stop_silent_t
        process = Popen(["gstdbuf", "-oL", CMD], stdout=PIPE)
        timerStart = time.time()
        detected_phrase = bytes()

        line = bytes()
        timeout_time = 2 * stop_if_silent_time
        while time.time() - timerStart < detection_time and process.poll()\
                is None:
            PROCESS_RUNNING = True
            signal.alarm(timeout_time)
            # This blocks until it receives a newline.
            try:
                if (process.stdout is not None):
                    line = process.stdout.readline()
            except TimeoutOfFunction:
                PROCESS_RUNNING = False
                process.terminate()
            print(type(line))
            if line != bytes():
                timeout_time = stop_if_silent_time
                print(line)
                detected_phrase = line
            else:
                print("????")
            # print(line)
            # last_detected_t = time.time()
        print("out_of_loop")
        process.terminate()
        PROCESS_RUNNING = False
        # last_detected = process.stdout.read()
        # print(last_detected)
        print(detected_phrase)
        print(str(detected_phrase)[2:-3])
        return str(detected_phrase)[2:-3]

# process.communicate() # close process' stream, wait for it to exit


class TimeoutOfFunction(Exception):
    pass


def handler(signum, frame):  # type: ignore
    print("wow it worked")
    if PROCESS_RUNNING is True:
        raise TimeoutOfFunction()


signal.signal(signal.SIGALRM, handler)  # type: ignore


if __name__ == '__main__':
    s = Speech()
    s.startSpeechRecognition(8)
