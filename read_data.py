import os
import time

path = '/Users/chonein/Downloads'


right = False
left = False
def raised_hands():
    global right, left
    lst = os.listdir(path)
    for f in lst:
        print(f'{path}/{f}')
        if f[-2:] and (f[0:2] == 'ri' or f[0:2] == 'le'):
            with open(f'{path}/{f}', 'r') as f_name:
                read = f_name.read()
                if len(read) > 3:
                    if f[0:2] == 'le' and float(read[7:11]) > 0.8:
                        left = True
                    else: 
                        left = False
                    if f[0:2] == 'ri' and float(read[7:11]) > 0.8:
                        right = True
                    else:
                        right = False
    for f in lst:
        os.remove(f'{path}/{f}')
    return {'right': right, 'left': left}

while(True):
    print(raised_hands())
    time.sleep(1)
# print(lst)
