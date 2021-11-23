# type: ignore
import random
import time

class HandRaise:
    def __init__(self) -> None:
        pass
    
    def read_status(self, file_name):
        try:
            with open(file_name, 'r') as f_name:
                lst = f_name.readlines()
                if len(lst) == 0:
                    return False
                lst = [float(element.strip()) for element in lst]
                for idx, element in enumerate(lst):
                    if idx < 3 and element > 0.8:
                        return False
                    elif idx >= 3 and element < 0.8:
                        return False
                print(lst)
                return True
                # return lst
        except FileNotFoundError:
            raise FileNotFoundError()
    
    def get_right_hand_status(self):
        return self.read_status('right_side_status.txt')

    def get_left_hand_status(self):
        return self.read_status('left_side_status.txt')
    
    def get_first_hand_raiser(self):
        """
            returns: str:
                    "right": right raised hand
                    "left": left raised hand
                    "low": no hand were raised
        """
        right = self.get_right_hand_status()
        left = self.get_left_hand_status()
        # print(right, left)
        if right is False and left is False:
            return "low"
        elif right is True and left is True:
            return random.choice(["right", "left"])
        elif right is True:
            return "right"
        else:
            return "left"



if __name__ == '__main__':
    h = HandRaise()
    time.sleep(5)
    print("started")
    # prev = False
    # while True:
    #     val = h.read_status('right_side_status.txt')
    #     if not (prev is False and val is False):
    #         print(val)
    #         prev = val
        # print(h.read_status('right_side_status.txt'))
    prev_val = "low"
    val = 'low'
    while val == "low":
        val = h.get_first_hand_raiser()
        # if not (val == "low" and prev_val == "low"):
    print(val)
    # prev_val = val
